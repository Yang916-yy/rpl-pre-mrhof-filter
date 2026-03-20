/*
 * Copyright (c) 2026, Zhaoyang Wang
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in the
 *    documentation and/or other materials provided with the distribution.
 * 3. Neither the name of the copyright holder nor the names of its
 *    contributors may be used to endorse or promote products derived
 *    from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
 * FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
 * COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
 * ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
 * OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#include "net/routing/rpl-lite/rpl-gate.h"

#include <string.h>
#include <stdio.h>

#include "net/link-stats.h"
#include "net/routing/rpl-lite/rpl-neighbor.h"
#include "os/sys/node-id.h"
#include "rpl-gate-prior-data.h"

/* Log configuration */
#include "sys/log.h"
#define LOG_MODULE "RPL Gate"
#define LOG_LEVEL LOG_LEVEL_RPL

#define RPL_GATE_LOG_INTERVAL (30 * CLOCK_SECOND)

typedef enum {
  EDGE_TIER_NEAR_OPTIMAL = 0,
  EDGE_TIER_MID_BAND = 1,
  EDGE_TIER_FORBIDDEN = 2
} edge_tier_t;

typedef struct {
  uint16_t child_id;
  uint16_t parent_id;
  int32_t etx_q8;
  int32_t etx_avg_q8;
  int32_t etx_var_q8;
  int32_t local_cost_q8;
  int32_t progress_q8;
  int32_t path_proxy_q8;
  int32_t geo_slack_q8;
  int32_t static_score_q8;
  int32_t etx_degrade_q8;
  int32_t dynamic_score_q8;
  int32_t dynamic_prev_q8;
  int32_t dynamic_shock_q8;
  uint8_t prior_valid;
  uint8_t hard_pruned;
  uint8_t frozen;
  uint8_t freeze_timer;
  uint8_t bad_counter;
  uint8_t good_counter;
  edge_tier_t tier;
} edge_gate_state_t;

typedef struct {
  uint8_t used;
  uint32_t last_round_seen;
  edge_gate_state_t state;
} edge_gate_slot_t;

typedef struct {
  uint8_t used;
  uint16_t parent_id;
} round_parent_entry_t;

typedef struct {
  uint32_t total_parent_comparisons;
  uint32_t parent_switch_count;
  uint32_t hard_pruned_edges;
  uint32_t hard_pruned_peak;
  uint32_t frozen_edges;
  uint32_t frozen_peak;
  uint32_t recovery_fallbacks;
  uint32_t usable_rounds;
  uint32_t mid_rounds;
  uint32_t recovery_rounds;
  uint32_t no_parent_rounds;
  uint32_t reconvergence_count;
  uint32_t reconvergence_last_ms;
  uint32_t reconvergence_sum_ms;
  uint32_t mid_observed;
  uint32_t mid_dynamic_max;
  uint32_t mid_shock_max;
} rpl_gate_metrics_t;

static edge_gate_slot_t state_table[RPL_GATE_MAX_STATES];
static round_parent_entry_t round_parents[NBR_TABLE_MAX_NEIGHBORS];
static rpl_gate_metrics_t metrics_state;
static uint8_t round_finalized;
static uint32_t round_seq;
static uint8_t recovery_active;
static clock_time_t recovery_start_time;
static struct ctimer metrics_log_timer;

static void schedule_metrics_log(void);
static void metrics_log_timer_cb(void *ptr);
static void emit_metrics_snapshot(void);
static void emit_config_snapshot(void);

static uint16_t
neighbor_id(rpl_nbr_t *nbr)
{
  const linkaddr_t *lladdr = rpl_neighbor_get_lladdr(nbr);

  if(lladdr == NULL) {
    return 0;
  }

  return lladdr->u8[LINKADDR_SIZE - 1] + (lladdr->u8[LINKADDR_SIZE - 2] << 8);
}

static int32_t
clamp_non_negative(int32_t value)
{
  return value < 0 ? 0 : value;
}

static edge_gate_slot_t *
find_slot(uint16_t child_id, uint16_t parent_id)
{
  uint16_t i;

  for(i = 0; i < RPL_GATE_MAX_STATES; i++) {
    if(state_table[i].used &&
       state_table[i].state.child_id == child_id &&
       state_table[i].state.parent_id == parent_id) {
      return &state_table[i];
    }
  }

  return NULL;
}

static edge_gate_slot_t *
touch_slot(uint16_t child_id, uint16_t parent_id)
{
  uint16_t i;
  edge_gate_slot_t *slot = find_slot(child_id, parent_id);

  if(slot != NULL) {
    return slot;
  }

  for(i = 0; i < RPL_GATE_MAX_STATES; i++) {
    if(!state_table[i].used) {
      memset(&state_table[i], 0, sizeof(state_table[i]));
      state_table[i].used = 1;
      state_table[i].state.child_id = child_id;
      state_table[i].state.parent_id = parent_id;
      state_table[i].state.tier = EDGE_TIER_MID_BAND;
      return &state_table[i];
    }
  }

  return NULL;
}

static int
prior_distance_q8(uint16_t id, int32_t *out)
{
  if(!RPL_GATE_PRIOR_ENABLED || out == NULL || id > RPL_GATE_PRIOR_MAX_NODE_ID) {
    return 0;
  }
  *out = rpl_gate_prior_d_q8[id];
  return *out > 0 || id == RPL_GATE_PRIOR_ROOT_ID;
}

static int
prior_struct_cost_q8(uint16_t child_id, uint16_t parent_id, int32_t *out)
{
  size_t stride = (size_t)RPL_GATE_PRIOR_MAX_NODE_ID + 1;
  size_t index;

  if(!RPL_GATE_PRIOR_ENABLED || out == NULL ||
     child_id > RPL_GATE_PRIOR_MAX_NODE_ID ||
     parent_id > RPL_GATE_PRIOR_MAX_NODE_ID) {
    return 0;
  }

  index = (size_t)child_id * stride + parent_id;
  *out = rpl_gate_prior_struct_cost_q8[index];
  return *out > 0;
}

static edge_tier_t
classify_survivor_tier(int32_t proxy_margin_q8)
{
  if(proxy_margin_q8 <= RPL_GATE_T_NEAR_Q8) {
    return EDGE_TIER_NEAR_OPTIMAL;
  }
  return EDGE_TIER_MID_BAND;
}

static void
recompute_metrics(void)
{
  uint16_t i;
  uint32_t hard_pruned = 0;
  uint32_t frozen = 0;

  for(i = 0; i < RPL_GATE_MAX_STATES; i++) {
    if(state_table[i].used) {
      if(state_table[i].state.hard_pruned) {
        hard_pruned++;
      }
      if(state_table[i].state.frozen) {
        frozen++;
      }
    }
  }

  metrics_state.hard_pruned_edges = hard_pruned;
  metrics_state.frozen_edges = frozen;
  if(hard_pruned > metrics_state.hard_pruned_peak) {
    metrics_state.hard_pruned_peak = hard_pruned;
  }
  if(frozen > metrics_state.frozen_peak) {
    metrics_state.frozen_peak = frozen;
  }
}

static void
add_round_parent(uint16_t parent_id)
{
  uint16_t i;

  for(i = 0; i < NBR_TABLE_MAX_NEIGHBORS; i++) {
    if(round_parents[i].used && round_parents[i].parent_id == parent_id) {
      return;
    }
  }

  for(i = 0; i < NBR_TABLE_MAX_NEIGHBORS; i++) {
    if(!round_parents[i].used) {
      round_parents[i].used = 1;
      round_parents[i].parent_id = parent_id;
      return;
    }
  }
}

static void
update_static_state(edge_gate_state_t *state)
{
  int32_t child_d_q8;
  int32_t parent_d_q8;
  int32_t struct_cost_q8;

  state->prior_valid = 0;
  state->local_cost_q8 = 0;
  state->progress_q8 = 0;
  state->path_proxy_q8 = 0x3fffffff;
  state->geo_slack_q8 = RPL_GATE_T_NEAR_Q8;
  state->static_score_q8 = state->geo_slack_q8;
  state->tier = EDGE_TIER_MID_BAND;
  state->hard_pruned = 0;

  if(!prior_distance_q8(state->child_id, &child_d_q8) ||
     !prior_distance_q8(state->parent_id, &parent_d_q8) ||
     !prior_struct_cost_q8(state->child_id, state->parent_id, &struct_cost_q8)) {
    return;
  }

  state->prior_valid = 1;
  state->local_cost_q8 = struct_cost_q8;
  state->progress_q8 = child_d_q8 - parent_d_q8;
  state->path_proxy_q8 = parent_d_q8 + struct_cost_q8;
  state->geo_slack_q8 = clamp_non_negative(state->path_proxy_q8 - child_d_q8);
  state->static_score_q8 = state->geo_slack_q8;
}

static void
update_dynamic_state(edge_gate_state_t *state, rpl_nbr_t *nbr)
{
  const struct link_stats *stats = rpl_neighbor_get_link_stats(nbr);
  int32_t rel_degrade_q8 = 0;
  int32_t prev_dynamic_q8 = state->dynamic_score_q8;

  if(stats == NULL || stats->etx == 0) {
    state->etx_degrade_q8 = 0;
    state->dynamic_score_q8 = 0;
    state->dynamic_prev_q8 = prev_dynamic_q8;
    state->dynamic_shock_q8 = 0;
    if(!RPL_GATE_ENABLE_SOFT_GATING) {
      state->frozen = 0;
      state->freeze_timer = 0;
      state->bad_counter = 0;
      state->good_counter = 0;
    }
    return;
  }

  state->etx_q8 = (int32_t)stats->etx << 1;
  if(state->etx_avg_q8 == 0) {
    state->etx_avg_q8 = state->etx_q8;
    state->etx_var_q8 = 0;
  } else {
    state->etx_avg_q8 = ((state->etx_avg_q8 * 3) + state->etx_q8) / 4;
    state->etx_var_q8 = ((state->etx_var_q8 * 3)
                        + clamp_non_negative(state->etx_q8 - state->etx_avg_q8)) / 4;
  }

  rel_degrade_q8 = clamp_non_negative(state->etx_q8 - state->etx_avg_q8);
  state->etx_degrade_q8 = rel_degrade_q8;
  state->dynamic_score_q8 = rel_degrade_q8 + state->etx_var_q8;
  state->dynamic_prev_q8 = prev_dynamic_q8;
  state->dynamic_shock_q8 = clamp_non_negative(state->dynamic_score_q8 - prev_dynamic_q8);
}

static void
apply_static_rules(void)
{
  uint16_t i;
  int32_t best_proxy_q8 = 0x3fffffff;

  for(i = 0; i < NBR_TABLE_MAX_NEIGHBORS; i++) {
    edge_gate_slot_t *slot;

    if(!round_parents[i].used) {
      continue;
    }

    slot = find_slot(node_id, round_parents[i].parent_id);
    if(slot == NULL || !slot->state.prior_valid || slot->state.progress_q8 <= 0) {
      continue;
    }

    if(slot->state.path_proxy_q8 < best_proxy_q8) {
      best_proxy_q8 = slot->state.path_proxy_q8;
    }
  }

  for(i = 0; i < NBR_TABLE_MAX_NEIGHBORS; i++) {
    edge_gate_slot_t *slot;
    edge_gate_state_t *state;
    int32_t proxy_margin_q8;

    if(!round_parents[i].used) {
      continue;
    }

    slot = find_slot(node_id, round_parents[i].parent_id);
    if(slot == NULL) {
      continue;
    }

    state = &slot->state;
    state->hard_pruned = 0;

    if(!state->prior_valid) {
      state->tier = EDGE_TIER_MID_BAND;
      continue;
    }

    if(state->progress_q8 <= 0) {
      state->hard_pruned = RPL_GATE_ENABLE_HARD_PRUNE;
    } else if(state->geo_slack_q8 > RPL_GATE_STRICT_SLACK_TAU_Q8) {
      state->hard_pruned = RPL_GATE_ENABLE_HARD_PRUNE;
    } else if(best_proxy_q8 != 0x3fffffff &&
              state->path_proxy_q8 > (best_proxy_q8 + RPL_GATE_T_MID_Q8)) {
      state->hard_pruned = RPL_GATE_ENABLE_HARD_PRUNE;
    }

    if(state->hard_pruned) {
      state->tier = EDGE_TIER_FORBIDDEN;
      continue;
    }

    proxy_margin_q8 = (best_proxy_q8 == 0x3fffffff) ? 0 : clamp_non_negative(state->path_proxy_q8 - best_proxy_q8);
    state->tier = classify_survivor_tier(proxy_margin_q8);

    if(state->tier == EDGE_TIER_MID_BAND) {
      metrics_state.mid_observed++;
      if((uint32_t)state->dynamic_score_q8 > metrics_state.mid_dynamic_max) {
        metrics_state.mid_dynamic_max = (uint32_t)state->dynamic_score_q8;
      }
      if((uint32_t)state->dynamic_shock_q8 > metrics_state.mid_shock_max) {
        metrics_state.mid_shock_max = (uint32_t)state->dynamic_shock_q8;
      }
    }

  }
}

static void
apply_relative_gating(void)
{
  uint16_t i;

  if(!RPL_GATE_ENABLE_SOFT_GATING) {
    for(i = 0; i < RPL_GATE_MAX_STATES; i++) {
      if(state_table[i].used) {
        state_table[i].state.frozen = 0;
        state_table[i].state.freeze_timer = 0;
        state_table[i].state.bad_counter = 0;
        state_table[i].state.good_counter = 0;
      }
    }
    return;
  }

  for(i = 0; i < NBR_TABLE_MAX_NEIGHBORS; i++) {
    edge_gate_slot_t *slot;
    edge_gate_state_t *state;
    uint8_t bad_sample = 0;
    uint8_t good_sample = 0;

    if(!round_parents[i].used) {
      continue;
    }

    slot = find_slot(node_id, round_parents[i].parent_id);
    if(slot == NULL || slot->state.hard_pruned) {
      continue;
    }

    state = &slot->state;

    if(state->tier == EDGE_TIER_NEAR_OPTIMAL) {
      bad_sample = (state->etx_q8 >= RPL_GATE_NEAR_ETX_OFF_Q8) &&
                   ((state->etx_degrade_q8 >= RPL_GATE_NEAR_DEGRADE_OFF_Q8) ||
                    (state->etx_var_q8 >= RPL_GATE_NEAR_DEGRADE_OFF_Q8));
      good_sample = (state->etx_q8 <= RPL_GATE_NEAR_ETX_ON_Q8) &&
                    (state->etx_degrade_q8 <= RPL_GATE_NEAR_DEGRADE_ON_Q8) &&
                    (state->etx_var_q8 <= RPL_GATE_NEAR_DEGRADE_ON_Q8);
    } else {
      bad_sample = (state->etx_degrade_q8 >= RPL_GATE_MID_DEGRADE_OFF_Q8) ||
                   (state->etx_var_q8 >= RPL_GATE_MID_DEGRADE_OFF_Q8);
      good_sample = (state->etx_degrade_q8 <= RPL_GATE_MID_DEGRADE_ON_Q8) &&
                    (state->etx_var_q8 <= RPL_GATE_MID_DEGRADE_ON_Q8);
    }

    if(bad_sample) {
      if(state->bad_counter < 0xff) {
        state->bad_counter++;
      }
      state->good_counter = 0;
    } else if(!state->frozen) {
      state->bad_counter = 0;
    }

    if(!state->frozen && state->bad_counter >= RPL_GATE_BAD_K) {
      state->frozen = 1;
      state->freeze_timer = RPL_GATE_MIN_FREEZE_TIME;
      state->bad_counter = 0;
      state->good_counter = 0;
    }

    if(state->frozen && state->freeze_timer == 0) {
      if(good_sample) {
        if(state->good_counter < 0xff) {
          state->good_counter++;
        }
        if(state->good_counter >= RPL_GATE_GOOD_M) {
          state->frozen = 0;
          state->good_counter = 0;
        }
      } else {
        state->good_counter = 0;
      }
    }
  }
}

static void
promote_reserve_edges(void)
{
  uint16_t i;
  uint16_t keep_count = 0;

  if(!RPL_GATE_ENABLE_HARD_PRUNE) {
    return;
  }

  for(i = 0; i < NBR_TABLE_MAX_NEIGHBORS; i++) {
    edge_gate_slot_t *slot;

    if(!round_parents[i].used) {
      continue;
    }

    slot = find_slot(node_id, round_parents[i].parent_id);
    if(slot != NULL && !slot->state.hard_pruned) {
      keep_count++;
    }
  }

  while(keep_count < RPL_GATE_MIN_RESERVE_PARENTS) {
    edge_gate_slot_t *best_forbidden = NULL;

    for(i = 0; i < NBR_TABLE_MAX_NEIGHBORS; i++) {
      edge_gate_slot_t *slot;

      if(!round_parents[i].used) {
        continue;
      }

      slot = find_slot(node_id, round_parents[i].parent_id);
      if(slot == NULL || !slot->state.hard_pruned) {
        continue;
      }

      if(best_forbidden == NULL ||
         slot->state.static_score_q8 < best_forbidden->state.static_score_q8) {
        best_forbidden = slot;
      }
    }

    if(best_forbidden == NULL) {
      break;
    }

    best_forbidden->state.hard_pruned = 0;
    best_forbidden->state.tier = EDGE_TIER_MID_BAND;
    keep_count++;
  }
}

void
rpl_gate_init(void)
{
  memset(state_table, 0, sizeof(state_table));
  memset(round_parents, 0, sizeof(round_parents));
  memset(&metrics_state, 0, sizeof(metrics_state));
  round_finalized = 0;
  round_seq = 0;
  recovery_active = 0;
  recovery_start_time = 0;
  emit_config_snapshot();
  schedule_metrics_log();
}

void
rpl_gate_begin_round(void)
{
  uint16_t i;

  if(!RPL_WITH_EDGE_GATE) {
    return;
  }

  round_seq++;
  round_finalized = 0;
  memset(round_parents, 0, sizeof(round_parents));

  for(i = 0; i < RPL_GATE_MAX_STATES; i++) {
    if(state_table[i].used && state_table[i].state.freeze_timer > 0) {
      state_table[i].state.freeze_timer--;
    }
  }
}

void
rpl_gate_observe_candidate(rpl_nbr_t *nbr)
{
  uint16_t parent_id;
  edge_gate_slot_t *slot;

  if(!RPL_WITH_EDGE_GATE || nbr == NULL || node_id == RPL_GATE_PRIOR_ROOT_ID) {
    return;
  }

  parent_id = neighbor_id(nbr);
  if(parent_id == 0) {
    return;
  }

  slot = touch_slot(node_id, parent_id);
  if(slot == NULL || slot->last_round_seen == round_seq) {
    return;
  }

  slot->last_round_seen = round_seq;
  update_static_state(&slot->state);
  update_dynamic_state(&slot->state, nbr);
  add_round_parent(parent_id);
}

void
rpl_gate_finalize_round(void)
{
  if(!RPL_WITH_EDGE_GATE || round_finalized) {
    return;
  }

  apply_static_rules();
  apply_relative_gating();
  promote_reserve_edges();
  recompute_metrics();
  round_finalized = 1;
}

int
rpl_gate_parent_allowed(rpl_nbr_t *nbr, rpl_gate_filter_mode_t mode)
{
  uint16_t parent_id;
  edge_gate_slot_t *slot;
  edge_gate_state_t *state;

  if(!RPL_WITH_EDGE_GATE || nbr == NULL || node_id == RPL_GATE_PRIOR_ROOT_ID) {
    return 1;
  }

  parent_id = neighbor_id(nbr);
  if(parent_id == 0) {
    return 1;
  }

  slot = find_slot(node_id, parent_id);
  if(slot == NULL) {
    return mode == RPL_GATE_FILTER_RECOVERY;
  }

  state = &slot->state;

  if(mode == RPL_GATE_FILTER_USABLE) {
    return !state->hard_pruned && !state->frozen;
  }

  if(mode == RPL_GATE_FILTER_MID_BAND) {
    return !state->hard_pruned && state->tier == EDGE_TIER_MID_BAND;
  }

  if(!state->hard_pruned && state->geo_slack_q8 <= RPL_GATE_RECOVERY_TAU_Q8) {
    return 1;
  }

  return 0;
}

void
rpl_gate_note_parent_comparison(void)
{
  metrics_state.total_parent_comparisons++;
}

void
rpl_gate_note_parent_switch(rpl_nbr_t *old_parent, rpl_nbr_t *new_parent)
{
  if(old_parent != new_parent) {
    metrics_state.parent_switch_count++;
  }
}

void
rpl_gate_note_selection_result(int found_parent, rpl_gate_filter_mode_t mode)
{
  if(!found_parent) {
    metrics_state.no_parent_rounds++;
    return;
  }

  if(mode == RPL_GATE_FILTER_USABLE) {
    metrics_state.usable_rounds++;
    if(recovery_active) {
      uint32_t delta_ms = (uint32_t)(((clock_time() - recovery_start_time) * 1000UL) / CLOCK_SECOND);
      metrics_state.reconvergence_count++;
      metrics_state.reconvergence_last_ms = delta_ms;
      metrics_state.reconvergence_sum_ms += delta_ms;
      recovery_active = 0;
      recovery_start_time = 0;
    }
    return;
  }

  if(mode == RPL_GATE_FILTER_MID_BAND) {
    metrics_state.mid_rounds++;
    return;
  }

  if(mode == RPL_GATE_FILTER_RECOVERY) {
    metrics_state.recovery_rounds++;
    metrics_state.recovery_fallbacks++;
    if(!recovery_active) {
      recovery_active = 1;
      recovery_start_time = clock_time();
    }
  }
}

static void
emit_config_snapshot(void)
{
  printf(
    "RPLCFG node=%u gate_on=%u hard_on=%u soft_on=%u prior_tx_range_q8=%u prior_hop_q8=%u t_near_q8=%u t_mid_q8=%u strict_slack_tau_q8=%u recovery_tau_q8=%u mid_degrade_on_q8=%u mid_degrade_off_q8=%u near_degrade_on_q8=%u near_degrade_off_q8=%u near_etx_on_q8=%u near_etx_off_q8=%u bad_k=%u good_m=%u min_freeze=%u reserve=%u\n",
    node_id,
    RPL_WITH_EDGE_GATE ? 1 : 0,
    RPL_GATE_ENABLE_HARD_PRUNE ? 1 : 0,
    RPL_GATE_ENABLE_SOFT_GATING ? 1 : 0,
    (unsigned)RPL_GATE_PRIOR_TX_RANGE_Q8,
    (unsigned)RPL_GATE_PRIOR_HOP_PENALTY_Q8,
    (unsigned)RPL_GATE_T_NEAR_Q8,
    (unsigned)RPL_GATE_T_MID_Q8,
    (unsigned)RPL_GATE_STRICT_SLACK_TAU_Q8,
    (unsigned)RPL_GATE_RECOVERY_TAU_Q8,
    (unsigned)RPL_GATE_MID_DEGRADE_ON_Q8,
    (unsigned)RPL_GATE_MID_DEGRADE_OFF_Q8,
    (unsigned)RPL_GATE_NEAR_DEGRADE_ON_Q8,
    (unsigned)RPL_GATE_NEAR_DEGRADE_OFF_Q8,
    (unsigned)RPL_GATE_NEAR_ETX_ON_Q8,
    (unsigned)RPL_GATE_NEAR_ETX_OFF_Q8,
    (unsigned)RPL_GATE_BAD_K,
    (unsigned)RPL_GATE_GOOD_M,
    (unsigned)RPL_GATE_MIN_FREEZE_TIME,
    (unsigned)RPL_GATE_MIN_RESERVE_PARENTS);
}

static void
emit_metrics_snapshot(void)
{
  unsigned long avg_reconv_ms = 0;

  if(metrics_state.reconvergence_count > 0) {
    avg_reconv_ms = metrics_state.reconvergence_sum_ms / metrics_state.reconvergence_count;
  }

  /* Re-emit the static gate configuration so late log collectors do not miss it. */
  emit_config_snapshot();

  printf(
    "RPLSTAT node=%u cmp=%lu sw=%lu hard_cur=%lu hard_peak=%lu frozen_cur=%lu frozen_peak=%lu fallback=%lu sel_usable=%lu sel_mid=%lu sel_recovery=%lu no_parent=%lu recov_cnt=%lu recov_last_ms=%lu recov_sum_ms=%lu recov_avg_ms=%lu mid_obs=%lu mid_dyn_max=%lu mid_shock_max=%lu\n",
    node_id,
    (unsigned long)metrics_state.total_parent_comparisons,
    (unsigned long)metrics_state.parent_switch_count,
    (unsigned long)metrics_state.hard_pruned_edges,
    (unsigned long)metrics_state.hard_pruned_peak,
    (unsigned long)metrics_state.frozen_edges,
    (unsigned long)metrics_state.frozen_peak,
    (unsigned long)metrics_state.recovery_fallbacks,
    (unsigned long)metrics_state.usable_rounds,
    (unsigned long)metrics_state.mid_rounds,
    (unsigned long)metrics_state.recovery_rounds,
    (unsigned long)metrics_state.no_parent_rounds,
    (unsigned long)metrics_state.reconvergence_count,
    (unsigned long)metrics_state.reconvergence_last_ms,
    (unsigned long)metrics_state.reconvergence_sum_ms,
    avg_reconv_ms,
    (unsigned long)metrics_state.mid_observed,
    (unsigned long)metrics_state.mid_dynamic_max,
    (unsigned long)metrics_state.mid_shock_max);
}

static void
metrics_log_timer_cb(void *ptr)
{
  (void)ptr;
  emit_metrics_snapshot();
  schedule_metrics_log();
}

static void
schedule_metrics_log(void)
{
  ctimer_set(&metrics_log_timer, RPL_GATE_LOG_INTERVAL, metrics_log_timer_cb, NULL);
}




