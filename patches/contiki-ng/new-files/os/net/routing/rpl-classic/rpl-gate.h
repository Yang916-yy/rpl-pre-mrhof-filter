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

#ifndef RPL_GATE_H_
#define RPL_GATE_H_

#include "net/routing/rpl-classic/rpl.h"

#ifdef RPL_CONF_WITH_EDGE_GATE
#define RPL_WITH_EDGE_GATE RPL_CONF_WITH_EDGE_GATE
#else
#define RPL_WITH_EDGE_GATE 0
#endif

#ifdef RPL_CONF_EDGE_GATE_ENABLE_HARD_PRUNE
#define RPL_GATE_ENABLE_HARD_PRUNE RPL_CONF_EDGE_GATE_ENABLE_HARD_PRUNE
#else
#define RPL_GATE_ENABLE_HARD_PRUNE 1
#endif

#ifdef RPL_CONF_EDGE_GATE_ENABLE_SOFT_GATING
#define RPL_GATE_ENABLE_SOFT_GATING RPL_CONF_EDGE_GATE_ENABLE_SOFT_GATING
#else
#define RPL_GATE_ENABLE_SOFT_GATING 1
#endif

#ifdef RPL_CONF_EDGE_GATE_MAX_STATES
#define RPL_GATE_MAX_STATES RPL_CONF_EDGE_GATE_MAX_STATES
#else
#define RPL_GATE_MAX_STATES 64
#endif

#ifdef RPL_CONF_EDGE_GATE_T_NEAR_Q8
#define RPL_GATE_T_NEAR_Q8 RPL_CONF_EDGE_GATE_T_NEAR_Q8
#else
#define RPL_GATE_T_NEAR_Q8 24
#endif

#ifdef RPL_CONF_EDGE_GATE_T_MID_Q8
#define RPL_GATE_T_MID_Q8 RPL_CONF_EDGE_GATE_T_MID_Q8
#else
#define RPL_GATE_T_MID_Q8 96
#endif

#ifdef RPL_CONF_EDGE_GATE_STRICT_SLACK_TAU_Q8
#define RPL_GATE_STRICT_SLACK_TAU_Q8 RPL_CONF_EDGE_GATE_STRICT_SLACK_TAU_Q8
#else
#define RPL_GATE_STRICT_SLACK_TAU_Q8 192
#endif

#ifdef RPL_CONF_EDGE_GATE_RECOVERY_TAU_Q8
#define RPL_GATE_RECOVERY_TAU_Q8 RPL_CONF_EDGE_GATE_RECOVERY_TAU_Q8
#else
#define RPL_GATE_RECOVERY_TAU_Q8 192
#endif

#ifdef RPL_CONF_EDGE_GATE_MID_DEGRADE_OFF_Q8
#define RPL_GATE_MID_DEGRADE_OFF_Q8 RPL_CONF_EDGE_GATE_MID_DEGRADE_OFF_Q8
#else
#define RPL_GATE_MID_DEGRADE_OFF_Q8 48
#endif

#ifdef RPL_CONF_EDGE_GATE_MID_DEGRADE_ON_Q8
#define RPL_GATE_MID_DEGRADE_ON_Q8 RPL_CONF_EDGE_GATE_MID_DEGRADE_ON_Q8
#else
#define RPL_GATE_MID_DEGRADE_ON_Q8 24
#endif

#ifdef RPL_CONF_EDGE_GATE_NEAR_DEGRADE_OFF_Q8
#define RPL_GATE_NEAR_DEGRADE_OFF_Q8 RPL_CONF_EDGE_GATE_NEAR_DEGRADE_OFF_Q8
#else
#define RPL_GATE_NEAR_DEGRADE_OFF_Q8 96
#endif

#ifdef RPL_CONF_EDGE_GATE_NEAR_DEGRADE_ON_Q8
#define RPL_GATE_NEAR_DEGRADE_ON_Q8 RPL_CONF_EDGE_GATE_NEAR_DEGRADE_ON_Q8
#else
#define RPL_GATE_NEAR_DEGRADE_ON_Q8 48
#endif

#ifdef RPL_CONF_EDGE_GATE_NEAR_ETX_OFF_Q8
#define RPL_GATE_NEAR_ETX_OFF_Q8 RPL_CONF_EDGE_GATE_NEAR_ETX_OFF_Q8
#else
#define RPL_GATE_NEAR_ETX_OFF_Q8 512
#endif

#ifdef RPL_CONF_EDGE_GATE_NEAR_ETX_ON_Q8
#define RPL_GATE_NEAR_ETX_ON_Q8 RPL_CONF_EDGE_GATE_NEAR_ETX_ON_Q8
#else
#define RPL_GATE_NEAR_ETX_ON_Q8 384
#endif

#ifdef RPL_CONF_EDGE_GATE_BAD_K
#define RPL_GATE_BAD_K RPL_CONF_EDGE_GATE_BAD_K
#else
#define RPL_GATE_BAD_K 4
#endif

#ifdef RPL_CONF_EDGE_GATE_GOOD_M
#define RPL_GATE_GOOD_M RPL_CONF_EDGE_GATE_GOOD_M
#else
#define RPL_GATE_GOOD_M 2
#endif

#ifdef RPL_CONF_EDGE_GATE_MIN_FREEZE_TIME
#define RPL_GATE_MIN_FREEZE_TIME RPL_CONF_EDGE_GATE_MIN_FREEZE_TIME
#else
#define RPL_GATE_MIN_FREEZE_TIME 2
#endif

#ifdef RPL_CONF_EDGE_GATE_MIN_RESERVE_PARENTS
#define RPL_GATE_MIN_RESERVE_PARENTS RPL_CONF_EDGE_GATE_MIN_RESERVE_PARENTS
#else
#define RPL_GATE_MIN_RESERVE_PARENTS 2
#endif

typedef enum {
  RPL_GATE_FILTER_USABLE = 0,
  RPL_GATE_FILTER_MID_BAND = 1,
  RPL_GATE_FILTER_RECOVERY = 2,
  RPL_GATE_FILTER_NONE = 255
} rpl_gate_filter_mode_t;

void rpl_gate_init(void);
void rpl_gate_begin_round(void);
void rpl_gate_observe_candidate(rpl_parent_t *parent);
void rpl_gate_finalize_round(void);
int rpl_gate_parent_allowed(rpl_parent_t *parent, rpl_gate_filter_mode_t mode);
void rpl_gate_note_parent_comparison(void);
void rpl_gate_note_parent_switch(rpl_parent_t *old_parent, rpl_parent_t *new_parent);
void rpl_gate_note_selection_result(int found_parent, rpl_gate_filter_mode_t mode);

#endif /* RPL_GATE_H_ */
