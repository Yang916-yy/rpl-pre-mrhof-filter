<?xml version='1.0' encoding='UTF-8'?>
<simconf version="2022112801">
  <simulation>
    <title>My simulation</title>
    <randomseed>1</randomseed>
    <motedelay_us>1000000</motedelay_us>
    <radiomedium>
      org.contikios.cooja.radiomediums.UDGM
      <transmitting_range>50.0</transmitting_range>
      <interference_range>50.0</interference_range>
      <success_ratio_tx>1.0</success_ratio_tx>
      <success_ratio_rx>1.0</success_ratio_rx>
    </radiomedium>
    <events>
      <logoutput>40000</logoutput>
    </events>
    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <description>Sender</description>
      <source>[CONFIG_DIR]/code/sender-node.c</source>
      <commands>$(MAKE) clean TARGET=cooja
$(MAKE) -j$(CPUS) sender-node.cooja TARGET=cooja</commands>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiVib</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRS232</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiBeeper</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiButton</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiPIR</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiClock</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiLED</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiCFS</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-7.19071602882406" y="34.96668248624779" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>2</id>
        </interface_config>
      </mote>
    </motetype>
    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <description>RPL root</description>
      <source>[CONFIG_DIR]/code/root-node.c</source>
      <commands>$(MAKE) clean TARGET=cooja
$(MAKE) -j$(CPUS) root-node.cooja TARGET=cooja</commands>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiVib</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRS232</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiBeeper</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiButton</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiPIR</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiClock</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiLED</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiCFS</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="8.0" y="2.0" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>1</id>
        </interface_config>
      </mote>
    </motetype>
    <motetype>
      org.contikios.cooja.contikimote.ContikiMoteType
      <description>Receiver</description>
      <source>[CONFIG_DIR]/code/receiver-node.c</source>
      <commands>$(MAKE) clean TARGET=cooja
$(MAKE) -j$(CPUS) receiver-node.cooja TARGET=cooja</commands>
      <moteinterface>org.contikios.cooja.interfaces.Position</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Battery</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiVib</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiMoteID</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRS232</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiBeeper</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.RimeAddress</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.IPAddress</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiRadio</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiButton</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiPIR</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiClock</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiLED</moteinterface>
      <moteinterface>org.contikios.cooja.contikimote.interfaces.ContikiCFS</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.Mote2MoteRelations</moteinterface>
      <moteinterface>org.contikios.cooja.interfaces.MoteAttributes</moteinterface>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>3</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>4</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>5</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>6</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>7</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>8</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>9</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>10</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>11</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>12</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>13</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>14</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>15</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>16</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>17</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>18</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>19</id>
        </interface_config>
      </mote>
      <mote>
        <interface_config>
          org.contikios.cooja.interfaces.Position
          <pos x="-17.870288882812428" y="4.581754854333804" />
        </interface_config>
        <interface_config>
          org.contikios.cooja.contikimote.interfaces.ContikiMoteID
          <id>20</id>
        </interface_config>
      </mote>
    </motetype>
  </simulation>
  <plugin>
    org.contikios.cooja.plugins.Visualizer
    <plugin_config>
      <moterelations>true</moterelations>
      <skin>org.contikios.cooja.plugins.skins.IDVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.UDGMVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.GridVisualizerSkin</skin>
      <skin>org.contikios.cooja.plugins.skins.MoteTypeVisualizerSkin</skin>
      <viewport>2.494541140753371 0.0 0.0 2.494541140753371 168.25302383129448 116.2254386098645</viewport>
    </plugin_config>
    <bounds x="1" y="1" height="400" width="400" z="3" />
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.LogListener
    <plugin_config>
      <filter />
      <formatted_time />
      <coloring />
    </plugin_config>
    <bounds x="402" y="162" height="428" width="597" z="2" />
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.Notes
    <plugin_config>
      <notes>Enter notes here</notes>
      <decorations>true</decorations>
    </plugin_config>
    <bounds x="680" y="0" height="160" width="904" z="1" />
  </plugin>
  <plugin>
    org.contikios.cooja.plugins.ScriptRunner
    <plugin_config>
      <script>GENERATE_MSG(1000000, "moving root 2 hops away");
GENERATE_MSG(1500000, "moving root back");

lostMsgs = 0;

sendCount = 0;
recvCount = 0;
hopSum = 0;
delaySum = 0;
delayCount = 0;
jitterSum = 0;
prevDelay = -1;
firstRxTime = -1;
recoveryMs = -1;
eventMarkUs = -1;
recoveryHits = 0;
recoveryArmed = 0;
txSeq = 0;
txTimes = {};
delays = [];
dioCount = 0;
daoCount = 0;
disCount = 0;
rplStats = {};
rplConfig = {};
var parseKeyValueLine = function(line) {
  var parts = line.split(" ");
  var out = {};
  for(var i = 1; i &lt; parts.length; i++) {
    var kv = parts[i].split("=");
    if(kv.length == 2) {
      out[kv[0]] = parseInt(kv[1]);
    }
  }
  return out;
};
var parseRplStat = function(line) {
  var stat = parseKeyValueLine(line);
  if(stat["node"] !== undefined) {
    rplStats[stat["node"]] = stat;
  }
};
var parseRplCfg = function(line) {
  var cfg = parseKeyValueLine(line);
  for(var key in cfg) {
    rplConfig[key] = cfg[key];
  }
};
var sumRplStat = function(key) {
  var total = 0;
  for(var id in rplStats) {
    if(rplStats[id][key] !== undefined) {
      total += rplStats[id][key];
    }
  }
  return total;
};
var maxRplStat = function(key) {
  var best = 0;
  for(var id in rplStats) {
    if(rplStats[id][key] !== undefined &amp;&amp; rplStats[id][key] > best) {
      best = rplStats[id][key];
    }
  }
  return best;
};

TIMEOUT(10000000, delays.sort(function(a,b){return a-b;}); p95 = (delays.length > 0) ? delays[Math.floor(0.95*(delays.length-1))] : -1; lostCalc = (sendCount >= recvCount) ? (sendCount - recvCount) : 0; pdr = (sendCount > 0) ? (1.0*recvCount/sendCount) : 0; avgHops = (recvCount > 0) ? (1.0*hopSum/recvCount) : -1; avgDelay = (delayCount > 0) ? (delaySum/delayCount) : -1; jitter = (delayCount > 1) ? (jitterSum/(delayCount-1)) : -1; convMs = (firstRxTime >= 0) ? (firstRxTime/1000.0) : -1; recMs = recoveryMs; gateCmp = 0; gateSw = 0; gateHardCur = 0; gateHardPeak = 0; gateFrozenCur = 0; gateFrozenPeak = 0; gateFallback = 0; gateSelUsable = 0; gateSelMid = 0; gateSelRecovery = 0; gateNoParent = 0; gateRecovCnt = 0; gateRecovLast = 0; gateRecovSum = 0; gateMidObs = 0; gateMidDynMax = 0; gateMidShockMax = 0; for(var gateNode in rplStats) { gateStat = rplStats[gateNode]; if(gateStat["cmp"] !== undefined) { gateCmp += gateStat["cmp"]; } if(gateStat["sw"] !== undefined) { gateSw += gateStat["sw"]; } if(gateStat["hard_cur"] !== undefined) { gateHardCur += gateStat["hard_cur"]; } if(gateStat["hard_peak"] !== undefined) { gateHardPeak += gateStat["hard_peak"]; } if(gateStat["frozen_cur"] !== undefined) { gateFrozenCur += gateStat["frozen_cur"]; } if(gateStat["frozen_peak"] !== undefined) { gateFrozenPeak += gateStat["frozen_peak"]; } if(gateStat["fallback"] !== undefined) { gateFallback += gateStat["fallback"]; } if(gateStat["sel_usable"] !== undefined) { gateSelUsable += gateStat["sel_usable"]; } if(gateStat["sel_mid"] !== undefined) { gateSelMid += gateStat["sel_mid"]; } if(gateStat["sel_recovery"] !== undefined) { gateSelRecovery += gateStat["sel_recovery"]; } if(gateStat["no_parent"] !== undefined) { gateNoParent += gateStat["no_parent"]; } if(gateStat["recov_cnt"] !== undefined) { gateRecovCnt += gateStat["recov_cnt"]; } if(gateStat["recov_sum_ms"] !== undefined) { gateRecovSum += gateStat["recov_sum_ms"]; } if(gateStat["recov_last_ms"] !== undefined &amp;&amp; gateStat["recov_last_ms"] > gateRecovLast) { gateRecovLast = gateStat["recov_last_ms"]; } if(gateStat["mid_obs"] !== undefined) { gateMidObs += gateStat["mid_obs"]; } if(gateStat["mid_dyn_max"] !== undefined &amp;&amp; gateStat["mid_dyn_max"] > gateMidDynMax) { gateMidDynMax = gateStat["mid_dyn_max"]; } if(gateStat["mid_shock_max"] !== undefined &amp;&amp; gateStat["mid_shock_max"] > gateMidShockMax) { gateMidShockMax = gateStat["mid_shock_max"]; } } gateRecovAvg = (gateRecovCnt > 0) ? (1.0 * gateRecovSum / gateRecovCnt) : -1; gateOn = (rplConfig["gate_on"] !== undefined) ? rplConfig["gate_on"] : 0; gatePriorTx = (rplConfig["prior_tx_range_q8"] !== undefined) ? rplConfig["prior_tx_range_q8"] : 0; gatePriorHop = (rplConfig["prior_hop_q8"] !== undefined) ? rplConfig["prior_hop_q8"] : 0; gateTNear = (rplConfig["t_near_q8"] !== undefined) ? rplConfig["t_near_q8"] : 0; gateTMid = (rplConfig["t_mid_q8"] !== undefined) ? rplConfig["t_mid_q8"] : 0; gateRecoveryTau = (rplConfig["recovery_tau_q8"] !== undefined) ? rplConfig["recovery_tau_q8"] : 0; gateFreezeOn = (rplConfig["freeze_on_q8"] !== undefined) ? rplConfig["freeze_on_q8"] : 0; gateFreezeOff = (rplConfig["freeze_off_q8"] !== undefined) ? rplConfig["freeze_off_q8"] : 0; gateHighBad = (rplConfig["high_bad_q8"] !== undefined) ? rplConfig["high_bad_q8"] : 0; gateShockOn = (rplConfig["shock_on_q8"] !== undefined) ? rplConfig["shock_on_q8"] : 0; gateShockOff = (rplConfig["shock_off_q8"] !== undefined) ? rplConfig["shock_off_q8"] : 0; gateMidDegOn = (rplConfig["mid_degrade_on_q8"] !== undefined) ? rplConfig["mid_degrade_on_q8"] : 0; gateMidDegOff = (rplConfig["mid_degrade_off_q8"] !== undefined) ? rplConfig["mid_degrade_off_q8"] : 0; gateNearDegOn = (rplConfig["near_degrade_on_q8"] !== undefined) ? rplConfig["near_degrade_on_q8"] : 0; gateNearDegOff = (rplConfig["near_degrade_off_q8"] !== undefined) ? rplConfig["near_degrade_off_q8"] : 0; gateNearEtxOn = (rplConfig["near_etx_on_q8"] !== undefined) ? rplConfig["near_etx_on_q8"] : 0; gateNearEtxOff = (rplConfig["near_etx_off_q8"] !== undefined) ? rplConfig["near_etx_off_q8"] : 0; gateBadK = (rplConfig["bad_k"] !== undefined) ? rplConfig["bad_k"] : 0; gateGoodM = (rplConfig["good_m"] !== undefined) ? rplConfig["good_m"] : 0; gateMinFreeze = (rplConfig["min_freeze"] !== undefined) ? rplConfig["min_freeze"] : 0; gateReserve = (rplConfig["reserve"] !== undefined) ? rplConfig["reserve"] : 0; log.log("METRIC send="+sendCount+" recv="+recvCount+" lost="+lostCalc+" pdr="+pdr.toFixed(6)+" avg_delay_ms="+avgDelay.toFixed(3)+" p95_delay_ms="+p95.toFixed(3)+" jitter_ms="+jitter.toFixed(3)+" avg_hops="+avgHops.toFixed(3)+" conv_ms="+convMs.toFixed(3)+" recov_ms="+recMs.toFixed(3)+" dio="+dioCount+" dao="+daoCount+" dis="+disCount+" gate_on="+gateOn+" gate_prior_tx_range_q8="+gatePriorTx+" gate_prior_hop_q8="+gatePriorHop+" gate_t_near_q8="+gateTNear+" gate_t_mid_q8="+gateTMid+" gate_recovery_tau_q8="+gateRecoveryTau+" gate_freeze_on_q8="+gateFreezeOn+" gate_freeze_off_q8="+gateFreezeOff+" gate_high_bad_q8="+gateHighBad+" gate_shock_on_q8="+gateShockOn+" gate_shock_off_q8="+gateShockOff+" gate_mid_degrade_on_q8="+gateMidDegOn+" gate_mid_degrade_off_q8="+gateMidDegOff+" gate_near_degrade_on_q8="+gateNearDegOn+" gate_near_degrade_off_q8="+gateNearDegOff+" gate_near_etx_on_q8="+gateNearEtxOn+" gate_near_etx_off_q8="+gateNearEtxOff+" gate_bad_k="+gateBadK+" gate_good_m="+gateGoodM+" gate_min_freeze="+gateMinFreeze+" gate_reserve="+gateReserve+" gate_cmp="+gateCmp+" gate_sw="+gateSw+" gate_hard_cur="+gateHardCur+" gate_hard_peak="+gateHardPeak+" gate_frozen_cur="+gateFrozenCur+" gate_frozen_peak="+gateFrozenPeak+" gate_fallback="+gateFallback+" gate_sel_usable="+gateSelUsable+" gate_sel_mid="+gateSelMid+" gate_sel_recovery="+gateSelRecovery+" gate_no_parent="+gateNoParent+" gate_recov_cnt="+gateRecovCnt+" gate_recov_last_ms="+gateRecovLast+" gate_recov_sum_ms="+gateRecovSum+" gate_recov_avg_ms="+gateRecovAvg.toFixed(3)+" gate_mid_obs="+gateMidObs+" gate_mid_dyn_max="+gateMidDynMax+" gate_mid_shock_max="+gateMidShockMax+"\n"); log.testOK(); );

lastMsg = -1;
packets = "_________";
hops = 0;
lastMsgHops = -1;

while(true) {
    YIELD();
    if(msg.indexOf("RPLTX:DIO") >= 0) { dioCount++; }
    if(msg.indexOf("RPLTX:DAO") >= 0) { daoCount++; }
    if(msg.indexOf("RPLTX:DIS") >= 0) { disCount++; }
    if(msg.indexOf("RPLSTAT ") == 0) { parseRplStat(msg); }
    if(msg.indexOf("RPLCFG ") == 0) { parseRplCfg(msg); }
    if(msg.equals("moving root 2 hops away")) {
        var root = sim.getMoteWithID(1);
        root.getInterfaces().getPosition().setCoordinates(5, -20, 0);
        log.log("moving root 2 hops away\n");
        eventMarkUs = -1;
        recoveryHits = 0;
        recoveryArmed = 0;
    } else if(msg.equals("moving root back")) {
        var root = sim.getMoteWithID(1);
        root.getInterfaces().getPosition().setCoordinates(8, 2, 0);
        log.log("moving root back\n");
        eventMarkUs = time;
        recoveryHits = 0;
        recoveryArmed = 1;
    } else if(msg.startsWith("Sending")) {
        txTimes[txSeq] = time;
        txSeq++;
        sendCount++;
        hops = 0;
    } else if(msg.startsWith("#L") &amp;&amp; msg.endsWith("1; red")) {
        hops++;
    } else if(msg.startsWith("Data")) {
        data = msg.split(" ");
        num = parseInt(data[14]);
        recvCount++;
        hopSum += hops;
        if(firstRxTime &lt; 0) { firstRxTime = time; }
        if((recoveryArmed == 1) &amp;&amp; (eventMarkUs >= 0) &amp;&amp; (recoveryMs &lt; 0)) {
          expExpected = lastMsg + 1;
          if(num == expExpected) {
            recoveryHits++;
          } else {
            recoveryHits = 1;
          }
          if(recoveryHits >= 3) {
            recoveryMs = (time - eventMarkUs) / 1000.0;
            eventMarkUs = -1;
            recoveryArmed = 0;
          }
        }
        if(txTimes[num] !== undefined) {
          d = (time - txTimes[num]) / 1000.0;
          if(d >= 0) {
            delaySum += d;
            delayCount++;
            delays.push(d);
            if(prevDelay >= 0) { jitterSum += Math.abs(d - prevDelay); }
            prevDelay = d;
          }
        }
        expExpected = lastMsg + 1;
        if(num != expExpected) {
          numMissed = num - expExpected;
          if(numMissed > 0) {
            lostMsgs += numMissed;
            log.log("Missed messages " + numMissed + " before " + num + "\n");
            for(i = 0; i &lt; numMissed; i++) {
                packets = packets.substr(0, lastMsg + i + 1).concat("_");
            }
          }
        }
        lastMsgHops = hops;
        packets = packets.substr(0, num).concat("*");
        log.log("" + hops + " " + packets + "\n");
        lastMsg = num;
    }
}</script>
      <active>true</active>
    </plugin_config>
    <bounds x="604" y="14" height="684" width="605" />
  </plugin>
</simconf>
