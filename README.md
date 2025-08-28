<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Consolidated Comparison Report</title>
<style>
    body { font-family: Arial, Helvetica, sans-serif; margin: 24px; }
    h1 { margin-bottom: 0; }
    h2 { margin-top: 28px; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; }
    th, td { border: 1px solid #ddd; padding: 6px; font-size: 14px; }
    th { background: #f7f7f7; }
    details { margin: 10px 0; }
    summary { font-weight: 600; cursor: pointer; }
    .grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
    .note { color: #666; font-size: 13px; }
    </style></head>
<body>
  <h1>Consolidated Comparison</h1>
  <div class="note">Input: filling_scheduler/examples/lots.csv</div>

  <h2>KPIs — All Runs</h2>
  <table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Run</th>
      <th>Makespan (h)</th>
      <th>Total Clean (h)</th>
      <th>Total Changeover (h)</th>
      <th>Total Fill (h)</th>
      <th>Lots Scheduled</th>
      <th>Clean Blocks</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Given (CSV Order)</td>
      <td>545.16</td>
      <td>120.00</td>
      <td>72.00</td>
      <td>353.16</td>
      <td>15</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Optimized (smart-pack)</td>
      <td>513.16</td>
      <td>96.00</td>
      <td>64.00</td>
      <td>353.16</td>
      <td>15</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Optimized (spt-pack)</td>
      <td>497.16</td>
      <td>96.00</td>
      <td>48.00</td>
      <td>353.16</td>
      <td>15</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Optimized (lpt-pack)</td>
      <td>497.16</td>
      <td>96.00</td>
      <td>48.00</td>
      <td>353.16</td>
      <td>15</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Optimized (cfs-pack)</td>
      <td>497.16</td>
      <td>96.00</td>
      <td>48.00</td>
      <td>353.16</td>
      <td>15</td>
      <td>4</td>
    </tr>
    <tr>
      <td>Optimized (hybrid)</td>
      <td>529.16</td>
      <td>120.00</td>
      <td>56.00</td>
      <td>353.16</td>
      <td>15</td>
      <td>5</td>
    </tr>
    <tr>
      <td>Optimized (milp)</td>
      <td>505.16</td>
      <td>96.00</td>
      <td>56.00</td>
      <td>353.16</td>
      <td>15</td>
      <td>4</td>
    </tr>
  </tbody>
</table>

  <h2>Delta to Given (per strategy)</h2>
  <h3>Delta to Given — smart-pack</h3>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Metric</th>
      <th>Given</th>
      <th>Optimized (smart-pack)</th>
      <th>Delta (Optimized (smart-pack) - Given)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Makespan (h)</td>
      <td>545.16</td>
      <td>513.16</td>
      <td>-32.00</td>
    </tr>
    <tr>
      <td>Total Clean (h)</td>
      <td>120.00</td>
      <td>96.00</td>
      <td>-24.00</td>
    </tr>
    <tr>
      <td>Total Changeover (h)</td>
      <td>72.00</td>
      <td>64.00</td>
      <td>-8.00</td>
    </tr>
    <tr>
      <td>Total Fill (h)</td>
      <td>353.16</td>
      <td>353.16</td>
      <td>0.00</td>
    </tr>
    <tr>
      <td>Lots Scheduled</td>
      <td>15</td>
      <td>15</td>
      <td></td>
    </tr>
    <tr>
      <td>Clean Blocks</td>
      <td>5</td>
      <td>4</td>
      <td></td>
    </tr>
  </tbody>
</table>
<h3>Delta to Given — spt-pack</h3>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Metric</th>
      <th>Given</th>
      <th>Optimized (spt-pack)</th>
      <th>Delta (Optimized (spt-pack) - Given)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Makespan (h)</td>
      <td>545.16</td>
      <td>497.16</td>
      <td>-48.00</td>
    </tr>
    <tr>
      <td>Total Clean (h)</td>
      <td>120.00</td>
      <td>96.00</td>
      <td>-24.00</td>
    </tr>
    <tr>
      <td>Total Changeover (h)</td>
      <td>72.00</td>
      <td>48.00</td>
      <td>-24.00</td>
    </tr>
    <tr>
      <td>Total Fill (h)</td>
      <td>353.16</td>
      <td>353.16</td>
      <td>0.00</td>
    </tr>
    <tr>
      <td>Lots Scheduled</td>
      <td>15</td>
      <td>15</td>
      <td></td>
    </tr>
    <tr>
      <td>Clean Blocks</td>
      <td>5</td>
      <td>4</td>
      <td></td>
    </tr>
  </tbody>
</table>
<h3>Delta to Given — lpt-pack</h3>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Metric</th>
      <th>Given</th>
      <th>Optimized (lpt-pack)</th>
      <th>Delta (Optimized (lpt-pack) - Given)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Makespan (h)</td>
      <td>545.16</td>
      <td>497.16</td>
      <td>-48.00</td>
    </tr>
    <tr>
      <td>Total Clean (h)</td>
      <td>120.00</td>
      <td>96.00</td>
      <td>-24.00</td>
    </tr>
    <tr>
      <td>Total Changeover (h)</td>
      <td>72.00</td>
      <td>48.00</td>
      <td>-24.00</td>
    </tr>
    <tr>
      <td>Total Fill (h)</td>
      <td>353.16</td>
      <td>353.16</td>
      <td>0.00</td>
    </tr>
    <tr>
      <td>Lots Scheduled</td>
      <td>15</td>
      <td>15</td>
      <td></td>
    </tr>
    <tr>
      <td>Clean Blocks</td>
      <td>5</td>
      <td>4</td>
      <td></td>
    </tr>
  </tbody>
</table>
<h3>Delta to Given — cfs-pack</h3>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Metric</th>
      <th>Given</th>
      <th>Optimized (cfs-pack)</th>
      <th>Delta (Optimized (cfs-pack) - Given)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Makespan (h)</td>
      <td>545.16</td>
      <td>497.16</td>
      <td>-48.00</td>
    </tr>
    <tr>
      <td>Total Clean (h)</td>
      <td>120.00</td>
      <td>96.00</td>
      <td>-24.00</td>
    </tr>
    <tr>
      <td>Total Changeover (h)</td>
      <td>72.00</td>
      <td>48.00</td>
      <td>-24.00</td>
    </tr>
    <tr>
      <td>Total Fill (h)</td>
      <td>353.16</td>
      <td>353.16</td>
      <td>0.00</td>
    </tr>
    <tr>
      <td>Lots Scheduled</td>
      <td>15</td>
      <td>15</td>
      <td></td>
    </tr>
    <tr>
      <td>Clean Blocks</td>
      <td>5</td>
      <td>4</td>
      <td></td>
    </tr>
  </tbody>
</table>
<h3>Delta to Given — hybrid</h3>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Metric</th>
      <th>Given</th>
      <th>Optimized (hybrid)</th>
      <th>Delta (Optimized (hybrid) - Given)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Makespan (h)</td>
      <td>545.16</td>
      <td>529.16</td>
      <td>-16.00</td>
    </tr>
    <tr>
      <td>Total Clean (h)</td>
      <td>120.00</td>
      <td>120.00</td>
      <td>0.00</td>
    </tr>
    <tr>
      <td>Total Changeover (h)</td>
      <td>72.00</td>
      <td>56.00</td>
      <td>-16.00</td>
    </tr>
    <tr>
      <td>Total Fill (h)</td>
      <td>353.16</td>
      <td>353.16</td>
      <td>0.00</td>
    </tr>
    <tr>
      <td>Lots Scheduled</td>
      <td>15</td>
      <td>15</td>
      <td></td>
    </tr>
    <tr>
      <td>Clean Blocks</td>
      <td>5</td>
      <td>5</td>
      <td></td>
    </tr>
  </tbody>
</table>
<h3>Delta to Given — milp</h3>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Metric</th>
      <th>Given</th>
      <th>Optimized (milp)</th>
      <th>Delta (Optimized (milp) - Given)</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Makespan (h)</td>
      <td>545.16</td>
      <td>505.16</td>
      <td>-40.00</td>
    </tr>
    <tr>
      <td>Total Clean (h)</td>
      <td>120.00</td>
      <td>96.00</td>
      <td>-24.00</td>
    </tr>
    <tr>
      <td>Total Changeover (h)</td>
      <td>72.00</td>
      <td>56.00</td>
      <td>-16.00</td>
    </tr>
    <tr>
      <td>Total Fill (h)</td>
      <td>353.16</td>
      <td>353.16</td>
      <td>0.00</td>
    </tr>
    <tr>
      <td>Lots Scheduled</td>
      <td>15</td>
      <td>15</td>
      <td></td>
    </tr>
    <tr>
      <td>Clean Blocks</td>
      <td>5</td>
      <td>4</td>
      <td></td>
    </tr>
  </tbody>
</table>

  <h2>Schedules</h2>
  
    <details open>
      <summary>Given Schedule (CSV order)</summary>
      <table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Start</th>
      <th>End</th>
      <th>Hours</th>
      <th>Activity</th>
      <th>Lot ID</th>
      <th>Type</th>
      <th>Note</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2025-01-01 08:00</td>
      <td>2025-01-02 08:00</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-02 08:00</td>
      <td>2025-01-02 13:01</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>A1</td>
      <td>VialE</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-02 13:01</td>
      <td>2025-01-02 21:01</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-02 21:01</td>
      <td>2025-01-04 18:12</td>
      <td>45.18</td>
      <td>FILL</td>
      <td>A2</td>
      <td>VialH</td>
      <td>900000 vials</td>
    </tr>
    <tr>
      <td>2025-01-04 18:12</td>
      <td>2025-01-05 02:12</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialE</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-05 02:12</td>
      <td>2025-01-06 15:51</td>
      <td>37.65</td>
      <td>FILL</td>
      <td>A3</td>
      <td>VialE</td>
      <td>750000 vials</td>
    </tr>
    <tr>
      <td>2025-01-06 15:51</td>
      <td>2025-01-07 15:51</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-07 15:51</td>
      <td>2025-01-09 18:03</td>
      <td>50.20</td>
      <td>FILL</td>
      <td>A4</td>
      <td>VialH</td>
      <td>1000000 vials</td>
    </tr>
    <tr>
      <td>2025-01-09 18:03</td>
      <td>2025-01-10 02:03</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialE</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-10 02:03</td>
      <td>2025-01-10 03:33</td>
      <td>1.51</td>
      <td>FILL</td>
      <td>A5</td>
      <td>VialE</td>
      <td>30000 vials</td>
    </tr>
    <tr>
      <td>2025-01-10 03:33</td>
      <td>2025-01-10 11:33</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-10 11:33</td>
      <td>2025-01-11 22:41</td>
      <td>35.14</td>
      <td>FILL</td>
      <td>B1</td>
      <td>VialH</td>
      <td>700000 vials</td>
    </tr>
    <tr>
      <td>2025-01-11 22:41</td>
      <td>2025-01-12 22:41</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-12 22:41</td>
      <td>2025-01-13 23:47</td>
      <td>25.10</td>
      <td>FILL</td>
      <td>B2</td>
      <td>VialH</td>
      <td>500000 vials</td>
    </tr>
    <tr>
      <td>2025-01-13 23:47</td>
      <td>2025-01-14 07:47</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialE</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-14 07:47</td>
      <td>2025-01-14 08:48</td>
      <td>1.00</td>
      <td>FILL</td>
      <td>C1</td>
      <td>VialE</td>
      <td>20000 vials</td>
    </tr>
    <tr>
      <td>2025-01-14 08:48</td>
      <td>2025-01-14 16:48</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-14 16:48</td>
      <td>2025-01-14 21:49</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>C2</td>
      <td>VialH</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-14 21:49</td>
      <td>2025-01-15 01:49</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-15 01:49</td>
      <td>2025-01-15 04:20</td>
      <td>2.51</td>
      <td>FILL</td>
      <td>C3</td>
      <td>VialH</td>
      <td>50000 vials</td>
    </tr>
    <tr>
      <td>2025-01-15 04:20</td>
      <td>2025-01-16 04:20</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-16 04:20</td>
      <td>2025-01-18 16:34</td>
      <td>60.24</td>
      <td>FILL</td>
      <td>C4</td>
      <td>VialE</td>
      <td>1200000 vials</td>
    </tr>
    <tr>
      <td>2025-01-18 16:34</td>
      <td>2025-01-19 00:34</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-19 00:34</td>
      <td>2025-01-20 07:56</td>
      <td>31.38</td>
      <td>FILL</td>
      <td>C5</td>
      <td>VialH</td>
      <td>625000 vials</td>
    </tr>
    <tr>
      <td>2025-01-20 07:56</td>
      <td>2025-01-20 11:56</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-20 11:56</td>
      <td>2025-01-20 12:27</td>
      <td>0.50</td>
      <td>FILL</td>
      <td>C6</td>
      <td>VialH</td>
      <td>10000 vials</td>
    </tr>
    <tr>
      <td>2025-01-20 12:27</td>
      <td>2025-01-21 12:27</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-21 12:27</td>
      <td>2025-01-23 04:36</td>
      <td>40.16</td>
      <td>FILL</td>
      <td>B3</td>
      <td>VialH</td>
      <td>800000 vials</td>
    </tr>
    <tr>
      <td>2025-01-23 04:36</td>
      <td>2025-01-23 12:36</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialE</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-23 12:36</td>
      <td>2025-01-24 01:09</td>
      <td>12.55</td>
      <td>FILL</td>
      <td>C7</td>
      <td>VialE</td>
      <td>250000 vials</td>
    </tr>
  </tbody>
</table>
    </details>
    

        <details>
          <summary>Optimized Schedule — smart-pack</summary>
          <table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Start</th>
      <th>End</th>
      <th>Hours</th>
      <th>Activity</th>
      <th>Lot ID</th>
      <th>Type</th>
      <th>Note</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2025-01-01 08:00</td>
      <td>2025-01-02 08:00</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-02 08:00</td>
      <td>2025-01-04 20:14</td>
      <td>60.24</td>
      <td>FILL</td>
      <td>C4</td>
      <td>VialE</td>
      <td>1200000 vials</td>
    </tr>
    <tr>
      <td>2025-01-04 20:14</td>
      <td>2025-01-05 04:14</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-05 04:14</td>
      <td>2025-01-07 01:25</td>
      <td>45.18</td>
      <td>FILL</td>
      <td>A2</td>
      <td>VialH</td>
      <td>900000 vials</td>
    </tr>
    <tr>
      <td>2025-01-07 01:25</td>
      <td>2025-01-07 05:25</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-07 05:25</td>
      <td>2025-01-07 07:55</td>
      <td>2.51</td>
      <td>FILL</td>
      <td>C3</td>
      <td>VialH</td>
      <td>50000 vials</td>
    </tr>
    <tr>
      <td>2025-01-07 07:55</td>
      <td>2025-01-08 07:55</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-08 07:55</td>
      <td>2025-01-10 10:07</td>
      <td>50.20</td>
      <td>FILL</td>
      <td>A4</td>
      <td>VialH</td>
      <td>1000000 vials</td>
    </tr>
    <tr>
      <td>2025-01-10 10:07</td>
      <td>2025-01-10 14:07</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-10 14:07</td>
      <td>2025-01-12 06:17</td>
      <td>40.16</td>
      <td>FILL</td>
      <td>B3</td>
      <td>VialH</td>
      <td>800000 vials</td>
    </tr>
    <tr>
      <td>2025-01-12 06:17</td>
      <td>2025-01-12 14:17</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialE</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-12 14:17</td>
      <td>2025-01-13 02:50</td>
      <td>12.55</td>
      <td>FILL</td>
      <td>C7</td>
      <td>VialE</td>
      <td>250000 vials</td>
    </tr>
    <tr>
      <td>2025-01-13 02:50</td>
      <td>2025-01-13 06:50</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-13 06:50</td>
      <td>2025-01-13 07:50</td>
      <td>1.00</td>
      <td>FILL</td>
      <td>C1</td>
      <td>VialE</td>
      <td>20000 vials</td>
    </tr>
    <tr>
      <td>2025-01-13 07:50</td>
      <td>2025-01-14 07:50</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-14 07:50</td>
      <td>2025-01-15 21:29</td>
      <td>37.65</td>
      <td>FILL</td>
      <td>A3</td>
      <td>VialE</td>
      <td>750000 vials</td>
    </tr>
    <tr>
      <td>2025-01-15 21:29</td>
      <td>2025-01-16 05:29</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-16 05:29</td>
      <td>2025-01-17 16:38</td>
      <td>35.14</td>
      <td>FILL</td>
      <td>B1</td>
      <td>VialH</td>
      <td>700000 vials</td>
    </tr>
    <tr>
      <td>2025-01-17 16:38</td>
      <td>2025-01-17 20:38</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-17 20:38</td>
      <td>2025-01-18 21:44</td>
      <td>25.10</td>
      <td>FILL</td>
      <td>B2</td>
      <td>VialH</td>
      <td>500000 vials</td>
    </tr>
    <tr>
      <td>2025-01-18 21:44</td>
      <td>2025-01-19 01:44</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-19 01:44</td>
      <td>2025-01-19 06:45</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>C2</td>
      <td>VialH</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-19 06:45</td>
      <td>2025-01-20 06:45</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-20 06:45</td>
      <td>2025-01-21 14:08</td>
      <td>31.38</td>
      <td>FILL</td>
      <td>C5</td>
      <td>VialH</td>
      <td>625000 vials</td>
    </tr>
    <tr>
      <td>2025-01-21 14:08</td>
      <td>2025-01-21 22:08</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialE</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-21 22:08</td>
      <td>2025-01-22 03:09</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>A1</td>
      <td>VialE</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-22 03:09</td>
      <td>2025-01-22 07:09</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-22 07:09</td>
      <td>2025-01-22 08:39</td>
      <td>1.51</td>
      <td>FILL</td>
      <td>A5</td>
      <td>VialE</td>
      <td>30000 vials</td>
    </tr>
    <tr>
      <td>2025-01-22 08:39</td>
      <td>2025-01-22 16:39</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-22 16:39</td>
      <td>2025-01-22 17:09</td>
      <td>0.50</td>
      <td>FILL</td>
      <td>C6</td>
      <td>VialH</td>
      <td>10000 vials</td>
    </tr>
  </tbody>
</table>
        </details>
        

        <details>
          <summary>Optimized Schedule — spt-pack</summary>
          <table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Start</th>
      <th>End</th>
      <th>Hours</th>
      <th>Activity</th>
      <th>Lot ID</th>
      <th>Type</th>
      <th>Note</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2025-01-01 08:00</td>
      <td>2025-01-02 08:00</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-02 08:00</td>
      <td>2025-01-02 08:30</td>
      <td>0.50</td>
      <td>FILL</td>
      <td>C6</td>
      <td>VialH</td>
      <td>10000 vials</td>
    </tr>
    <tr>
      <td>2025-01-02 08:30</td>
      <td>2025-01-02 12:30</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-02 12:30</td>
      <td>2025-01-02 15:00</td>
      <td>2.51</td>
      <td>FILL</td>
      <td>C3</td>
      <td>VialH</td>
      <td>50000 vials</td>
    </tr>
    <tr>
      <td>2025-01-02 15:00</td>
      <td>2025-01-02 19:00</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-02 19:00</td>
      <td>2025-01-03 00:01</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>C2</td>
      <td>VialH</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-03 00:01</td>
      <td>2025-01-03 04:01</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-03 04:01</td>
      <td>2025-01-04 05:07</td>
      <td>25.10</td>
      <td>FILL</td>
      <td>B2</td>
      <td>VialH</td>
      <td>500000 vials</td>
    </tr>
    <tr>
      <td>2025-01-04 05:07</td>
      <td>2025-01-04 09:07</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-04 09:07</td>
      <td>2025-01-05 16:30</td>
      <td>31.38</td>
      <td>FILL</td>
      <td>C5</td>
      <td>VialH</td>
      <td>625000 vials</td>
    </tr>
    <tr>
      <td>2025-01-05 16:30</td>
      <td>2025-01-05 20:30</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-05 20:30</td>
      <td>2025-01-07 07:38</td>
      <td>35.14</td>
      <td>FILL</td>
      <td>B1</td>
      <td>VialH</td>
      <td>700000 vials</td>
    </tr>
    <tr>
      <td>2025-01-07 07:38</td>
      <td>2025-01-08 07:38</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-08 07:38</td>
      <td>2025-01-09 23:48</td>
      <td>40.16</td>
      <td>FILL</td>
      <td>B3</td>
      <td>VialH</td>
      <td>800000 vials</td>
    </tr>
    <tr>
      <td>2025-01-09 23:48</td>
      <td>2025-01-10 03:48</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-10 03:48</td>
      <td>2025-01-12 00:59</td>
      <td>45.18</td>
      <td>FILL</td>
      <td>A2</td>
      <td>VialH</td>
      <td>900000 vials</td>
    </tr>
    <tr>
      <td>2025-01-12 00:59</td>
      <td>2025-01-12 08:59</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialE</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-12 08:59</td>
      <td>2025-01-12 09:59</td>
      <td>1.00</td>
      <td>FILL</td>
      <td>C1</td>
      <td>VialE</td>
      <td>20000 vials</td>
    </tr>
    <tr>
      <td>2025-01-12 09:59</td>
      <td>2025-01-12 13:59</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-12 13:59</td>
      <td>2025-01-12 15:30</td>
      <td>1.51</td>
      <td>FILL</td>
      <td>A5</td>
      <td>VialE</td>
      <td>30000 vials</td>
    </tr>
    <tr>
      <td>2025-01-12 15:30</td>
      <td>2025-01-12 19:30</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-12 19:30</td>
      <td>2025-01-13 00:31</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>A1</td>
      <td>VialE</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-13 00:31</td>
      <td>2025-01-14 00:31</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-14 00:31</td>
      <td>2025-01-14 13:04</td>
      <td>12.55</td>
      <td>FILL</td>
      <td>C7</td>
      <td>VialE</td>
      <td>250000 vials</td>
    </tr>
    <tr>
      <td>2025-01-14 13:04</td>
      <td>2025-01-14 17:04</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-14 17:04</td>
      <td>2025-01-16 06:43</td>
      <td>37.65</td>
      <td>FILL</td>
      <td>A3</td>
      <td>VialE</td>
      <td>750000 vials</td>
    </tr>
    <tr>
      <td>2025-01-16 06:43</td>
      <td>2025-01-16 10:43</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-16 10:43</td>
      <td>2025-01-18 22:57</td>
      <td>60.24</td>
      <td>FILL</td>
      <td>C4</td>
      <td>VialE</td>
      <td>1200000 vials</td>
    </tr>
    <tr>
      <td>2025-01-18 22:57</td>
      <td>2025-01-19 22:57</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-19 22:57</td>
      <td>2025-01-22 01:09</td>
      <td>50.20</td>
      <td>FILL</td>
      <td>A4</td>
      <td>VialH</td>
      <td>1000000 vials</td>
    </tr>
  </tbody>
</table>
        </details>
        

        <details>
          <summary>Optimized Schedule — lpt-pack</summary>
          <table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Start</th>
      <th>End</th>
      <th>Hours</th>
      <th>Activity</th>
      <th>Lot ID</th>
      <th>Type</th>
      <th>Note</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2025-01-01 08:00</td>
      <td>2025-01-02 08:00</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-02 08:00</td>
      <td>2025-01-04 20:14</td>
      <td>60.24</td>
      <td>FILL</td>
      <td>C4</td>
      <td>VialE</td>
      <td>1200000 vials</td>
    </tr>
    <tr>
      <td>2025-01-04 20:14</td>
      <td>2025-01-05 00:14</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-05 00:14</td>
      <td>2025-01-06 13:53</td>
      <td>37.65</td>
      <td>FILL</td>
      <td>A3</td>
      <td>VialE</td>
      <td>750000 vials</td>
    </tr>
    <tr>
      <td>2025-01-06 13:53</td>
      <td>2025-01-06 17:53</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-06 17:53</td>
      <td>2025-01-07 06:26</td>
      <td>12.55</td>
      <td>FILL</td>
      <td>C7</td>
      <td>VialE</td>
      <td>250000 vials</td>
    </tr>
    <tr>
      <td>2025-01-07 06:26</td>
      <td>2025-01-08 06:26</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-08 06:26</td>
      <td>2025-01-08 11:27</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>A1</td>
      <td>VialE</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-08 11:27</td>
      <td>2025-01-08 15:27</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-08 15:27</td>
      <td>2025-01-08 16:58</td>
      <td>1.51</td>
      <td>FILL</td>
      <td>A5</td>
      <td>VialE</td>
      <td>30000 vials</td>
    </tr>
    <tr>
      <td>2025-01-08 16:58</td>
      <td>2025-01-08 20:58</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-08 20:58</td>
      <td>2025-01-08 21:58</td>
      <td>1.00</td>
      <td>FILL</td>
      <td>C1</td>
      <td>VialE</td>
      <td>20000 vials</td>
    </tr>
    <tr>
      <td>2025-01-08 21:58</td>
      <td>2025-01-09 05:58</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-09 05:58</td>
      <td>2025-01-09 06:28</td>
      <td>0.50</td>
      <td>FILL</td>
      <td>C6</td>
      <td>VialH</td>
      <td>10000 vials</td>
    </tr>
    <tr>
      <td>2025-01-09 06:28</td>
      <td>2025-01-09 10:28</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-09 10:28</td>
      <td>2025-01-11 12:40</td>
      <td>50.20</td>
      <td>FILL</td>
      <td>A4</td>
      <td>VialH</td>
      <td>1000000 vials</td>
    </tr>
    <tr>
      <td>2025-01-11 12:40</td>
      <td>2025-01-11 16:40</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-11 16:40</td>
      <td>2025-01-13 03:48</td>
      <td>35.14</td>
      <td>FILL</td>
      <td>B1</td>
      <td>VialH</td>
      <td>700000 vials</td>
    </tr>
    <tr>
      <td>2025-01-13 03:48</td>
      <td>2025-01-14 03:48</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-14 03:48</td>
      <td>2025-01-15 11:11</td>
      <td>31.38</td>
      <td>FILL</td>
      <td>C5</td>
      <td>VialH</td>
      <td>625000 vials</td>
    </tr>
    <tr>
      <td>2025-01-15 11:11</td>
      <td>2025-01-15 15:11</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-15 15:11</td>
      <td>2025-01-16 16:17</td>
      <td>25.10</td>
      <td>FILL</td>
      <td>B2</td>
      <td>VialH</td>
      <td>500000 vials</td>
    </tr>
    <tr>
      <td>2025-01-16 16:17</td>
      <td>2025-01-16 20:17</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-16 20:17</td>
      <td>2025-01-17 01:18</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>C2</td>
      <td>VialH</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-17 01:18</td>
      <td>2025-01-17 05:18</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-17 05:18</td>
      <td>2025-01-17 07:49</td>
      <td>2.51</td>
      <td>FILL</td>
      <td>C3</td>
      <td>VialH</td>
      <td>50000 vials</td>
    </tr>
    <tr>
      <td>2025-01-17 07:49</td>
      <td>2025-01-18 07:49</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-18 07:49</td>
      <td>2025-01-20 05:00</td>
      <td>45.18</td>
      <td>FILL</td>
      <td>A2</td>
      <td>VialH</td>
      <td>900000 vials</td>
    </tr>
    <tr>
      <td>2025-01-20 05:00</td>
      <td>2025-01-20 09:00</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-20 09:00</td>
      <td>2025-01-22 01:09</td>
      <td>40.16</td>
      <td>FILL</td>
      <td>B3</td>
      <td>VialH</td>
      <td>800000 vials</td>
    </tr>
  </tbody>
</table>
        </details>
        

        <details>
          <summary>Optimized Schedule — cfs-pack</summary>
          <table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Start</th>
      <th>End</th>
      <th>Hours</th>
      <th>Activity</th>
      <th>Lot ID</th>
      <th>Type</th>
      <th>Note</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2025-01-01 08:00</td>
      <td>2025-01-02 08:00</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-02 08:00</td>
      <td>2025-01-04 10:12</td>
      <td>50.20</td>
      <td>FILL</td>
      <td>A4</td>
      <td>VialH</td>
      <td>1000000 vials</td>
    </tr>
    <tr>
      <td>2025-01-04 10:12</td>
      <td>2025-01-04 14:12</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-04 14:12</td>
      <td>2025-01-06 11:22</td>
      <td>45.18</td>
      <td>FILL</td>
      <td>A2</td>
      <td>VialH</td>
      <td>900000 vials</td>
    </tr>
    <tr>
      <td>2025-01-06 11:22</td>
      <td>2025-01-06 15:22</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-06 15:22</td>
      <td>2025-01-06 20:24</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>C2</td>
      <td>VialH</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-06 20:24</td>
      <td>2025-01-07 00:24</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-07 00:24</td>
      <td>2025-01-07 02:54</td>
      <td>2.51</td>
      <td>FILL</td>
      <td>C3</td>
      <td>VialH</td>
      <td>50000 vials</td>
    </tr>
    <tr>
      <td>2025-01-07 02:54</td>
      <td>2025-01-07 06:54</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-07 06:54</td>
      <td>2025-01-07 07:24</td>
      <td>0.50</td>
      <td>FILL</td>
      <td>C6</td>
      <td>VialH</td>
      <td>10000 vials</td>
    </tr>
    <tr>
      <td>2025-01-07 07:24</td>
      <td>2025-01-08 07:24</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-08 07:24</td>
      <td>2025-01-10 19:39</td>
      <td>60.24</td>
      <td>FILL</td>
      <td>C4</td>
      <td>VialE</td>
      <td>1200000 vials</td>
    </tr>
    <tr>
      <td>2025-01-10 19:39</td>
      <td>2025-01-10 23:39</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-10 23:39</td>
      <td>2025-01-12 13:18</td>
      <td>37.65</td>
      <td>FILL</td>
      <td>A3</td>
      <td>VialE</td>
      <td>750000 vials</td>
    </tr>
    <tr>
      <td>2025-01-12 13:18</td>
      <td>2025-01-12 17:18</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-12 17:18</td>
      <td>2025-01-13 05:51</td>
      <td>12.55</td>
      <td>FILL</td>
      <td>C7</td>
      <td>VialE</td>
      <td>250000 vials</td>
    </tr>
    <tr>
      <td>2025-01-13 05:51</td>
      <td>2025-01-14 05:51</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-14 05:51</td>
      <td>2025-01-14 10:52</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>A1</td>
      <td>VialE</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-14 10:52</td>
      <td>2025-01-14 14:52</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-14 14:52</td>
      <td>2025-01-14 16:22</td>
      <td>1.51</td>
      <td>FILL</td>
      <td>A5</td>
      <td>VialE</td>
      <td>30000 vials</td>
    </tr>
    <tr>
      <td>2025-01-14 16:22</td>
      <td>2025-01-14 20:22</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-14 20:22</td>
      <td>2025-01-14 21:23</td>
      <td>1.00</td>
      <td>FILL</td>
      <td>C1</td>
      <td>VialE</td>
      <td>20000 vials</td>
    </tr>
    <tr>
      <td>2025-01-14 21:23</td>
      <td>2025-01-15 05:23</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-15 05:23</td>
      <td>2025-01-16 21:32</td>
      <td>40.16</td>
      <td>FILL</td>
      <td>B3</td>
      <td>VialH</td>
      <td>800000 vials</td>
    </tr>
    <tr>
      <td>2025-01-16 21:32</td>
      <td>2025-01-17 01:32</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-17 01:32</td>
      <td>2025-01-18 12:41</td>
      <td>35.14</td>
      <td>FILL</td>
      <td>B1</td>
      <td>VialH</td>
      <td>700000 vials</td>
    </tr>
    <tr>
      <td>2025-01-18 12:41</td>
      <td>2025-01-19 12:41</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-19 12:41</td>
      <td>2025-01-20 20:03</td>
      <td>31.38</td>
      <td>FILL</td>
      <td>C5</td>
      <td>VialH</td>
      <td>625000 vials</td>
    </tr>
    <tr>
      <td>2025-01-20 20:03</td>
      <td>2025-01-21 00:03</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-21 00:03</td>
      <td>2025-01-22 01:09</td>
      <td>25.10</td>
      <td>FILL</td>
      <td>B2</td>
      <td>VialH</td>
      <td>500000 vials</td>
    </tr>
  </tbody>
</table>
        </details>
        

        <details>
          <summary>Optimized Schedule — hybrid</summary>
          <table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Start</th>
      <th>End</th>
      <th>Hours</th>
      <th>Activity</th>
      <th>Lot ID</th>
      <th>Type</th>
      <th>Note</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2025-01-01 08:00</td>
      <td>2025-01-02 08:00</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-02 08:00</td>
      <td>2025-01-04 20:14</td>
      <td>60.24</td>
      <td>FILL</td>
      <td>C4</td>
      <td>VialE</td>
      <td>1200000 vials</td>
    </tr>
    <tr>
      <td>2025-01-04 20:14</td>
      <td>2025-01-05 04:14</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-05 04:14</td>
      <td>2025-01-07 01:25</td>
      <td>45.18</td>
      <td>FILL</td>
      <td>A2</td>
      <td>VialH</td>
      <td>900000 vials</td>
    </tr>
    <tr>
      <td>2025-01-07 01:25</td>
      <td>2025-01-07 05:25</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-07 05:25</td>
      <td>2025-01-07 07:55</td>
      <td>2.51</td>
      <td>FILL</td>
      <td>C3</td>
      <td>VialH</td>
      <td>50000 vials</td>
    </tr>
    <tr>
      <td>2025-01-07 07:55</td>
      <td>2025-01-08 07:55</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-08 07:55</td>
      <td>2025-01-10 10:07</td>
      <td>50.20</td>
      <td>FILL</td>
      <td>A4</td>
      <td>VialH</td>
      <td>1000000 vials</td>
    </tr>
    <tr>
      <td>2025-01-10 10:07</td>
      <td>2025-01-10 14:07</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-10 14:07</td>
      <td>2025-01-12 06:17</td>
      <td>40.16</td>
      <td>FILL</td>
      <td>B3</td>
      <td>VialH</td>
      <td>800000 vials</td>
    </tr>
    <tr>
      <td>2025-01-12 06:17</td>
      <td>2025-01-12 14:17</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialE</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-12 14:17</td>
      <td>2025-01-13 02:50</td>
      <td>12.55</td>
      <td>FILL</td>
      <td>C7</td>
      <td>VialE</td>
      <td>250000 vials</td>
    </tr>
    <tr>
      <td>2025-01-13 02:50</td>
      <td>2025-01-13 06:50</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-13 06:50</td>
      <td>2025-01-13 07:50</td>
      <td>1.00</td>
      <td>FILL</td>
      <td>C1</td>
      <td>VialE</td>
      <td>20000 vials</td>
    </tr>
    <tr>
      <td>2025-01-13 07:50</td>
      <td>2025-01-14 07:50</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-14 07:50</td>
      <td>2025-01-15 21:29</td>
      <td>37.65</td>
      <td>FILL</td>
      <td>A3</td>
      <td>VialE</td>
      <td>750000 vials</td>
    </tr>
    <tr>
      <td>2025-01-15 21:29</td>
      <td>2025-01-16 05:29</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-16 05:29</td>
      <td>2025-01-17 16:38</td>
      <td>35.14</td>
      <td>FILL</td>
      <td>B1</td>
      <td>VialH</td>
      <td>700000 vials</td>
    </tr>
    <tr>
      <td>2025-01-17 16:38</td>
      <td>2025-01-17 20:38</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-17 20:38</td>
      <td>2025-01-18 21:44</td>
      <td>25.10</td>
      <td>FILL</td>
      <td>B2</td>
      <td>VialH</td>
      <td>500000 vials</td>
    </tr>
    <tr>
      <td>2025-01-18 21:44</td>
      <td>2025-01-19 01:44</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-19 01:44</td>
      <td>2025-01-19 06:45</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>C2</td>
      <td>VialH</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-19 06:45</td>
      <td>2025-01-20 06:45</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-20 06:45</td>
      <td>2025-01-21 14:08</td>
      <td>31.38</td>
      <td>FILL</td>
      <td>C5</td>
      <td>VialH</td>
      <td>625000 vials</td>
    </tr>
    <tr>
      <td>2025-01-21 14:08</td>
      <td>2025-01-21 22:08</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialE</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-21 22:08</td>
      <td>2025-01-22 03:09</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>A1</td>
      <td>VialE</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-22 03:09</td>
      <td>2025-01-22 07:09</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-22 07:09</td>
      <td>2025-01-22 08:39</td>
      <td>1.51</td>
      <td>FILL</td>
      <td>A5</td>
      <td>VialE</td>
      <td>30000 vials</td>
    </tr>
    <tr>
      <td>2025-01-22 08:39</td>
      <td>2025-01-23 08:39</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-23 08:39</td>
      <td>2025-01-23 09:09</td>
      <td>0.50</td>
      <td>FILL</td>
      <td>C6</td>
      <td>VialH</td>
      <td>10000 vials</td>
    </tr>
  </tbody>
</table>
        </details>
        

        <details>
          <summary>Optimized Schedule — milp</summary>
          <table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>Start</th>
      <th>End</th>
      <th>Hours</th>
      <th>Activity</th>
      <th>Lot ID</th>
      <th>Type</th>
      <th>Note</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>2025-01-01 08:00</td>
      <td>2025-01-02 08:00</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-02 08:00</td>
      <td>2025-01-04 00:09</td>
      <td>40.16</td>
      <td>FILL</td>
      <td>B3</td>
      <td>VialH</td>
      <td>800000 vials</td>
    </tr>
    <tr>
      <td>2025-01-04 00:09</td>
      <td>2025-01-04 04:09</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-04 04:09</td>
      <td>2025-01-04 04:39</td>
      <td>0.50</td>
      <td>FILL</td>
      <td>C6</td>
      <td>VialH</td>
      <td>10000 vials</td>
    </tr>
    <tr>
      <td>2025-01-04 04:39</td>
      <td>2025-01-04 08:39</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-04 08:39</td>
      <td>2025-01-04 13:40</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>C2</td>
      <td>VialH</td>
      <td>100000 vials</td>
    </tr>
    <tr>
      <td>2025-01-04 13:40</td>
      <td>2025-01-04 17:40</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-04 17:40</td>
      <td>2025-01-06 19:53</td>
      <td>50.20</td>
      <td>FILL</td>
      <td>A4</td>
      <td>VialH</td>
      <td>1000000 vials</td>
    </tr>
    <tr>
      <td>2025-01-06 19:53</td>
      <td>2025-01-07 03:53</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialE</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-07 03:53</td>
      <td>2025-01-07 05:23</td>
      <td>1.51</td>
      <td>FILL</td>
      <td>A5</td>
      <td>VialE</td>
      <td>30000 vials</td>
    </tr>
    <tr>
      <td>2025-01-07 05:23</td>
      <td>2025-01-08 05:23</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-08 05:23</td>
      <td>2025-01-08 17:56</td>
      <td>12.55</td>
      <td>FILL</td>
      <td>C7</td>
      <td>VialE</td>
      <td>250000 vials</td>
    </tr>
    <tr>
      <td>2025-01-08 17:56</td>
      <td>2025-01-08 21:56</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-08 21:56</td>
      <td>2025-01-11 10:10</td>
      <td>60.24</td>
      <td>FILL</td>
      <td>C4</td>
      <td>VialE</td>
      <td>1200000 vials</td>
    </tr>
    <tr>
      <td>2025-01-11 10:10</td>
      <td>2025-01-11 18:10</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialH</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-11 18:10</td>
      <td>2025-01-12 19:16</td>
      <td>25.10</td>
      <td>FILL</td>
      <td>B2</td>
      <td>VialH</td>
      <td>500000 vials</td>
    </tr>
    <tr>
      <td>2025-01-12 19:16</td>
      <td>2025-01-13 19:16</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-13 19:16</td>
      <td>2025-01-15 02:39</td>
      <td>31.38</td>
      <td>FILL</td>
      <td>C5</td>
      <td>VialH</td>
      <td>625000 vials</td>
    </tr>
    <tr>
      <td>2025-01-15 02:39</td>
      <td>2025-01-15 06:39</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-15 06:39</td>
      <td>2025-01-17 03:50</td>
      <td>45.18</td>
      <td>FILL</td>
      <td>A2</td>
      <td>VialH</td>
      <td>900000 vials</td>
    </tr>
    <tr>
      <td>2025-01-17 03:50</td>
      <td>2025-01-17 07:50</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialH</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-17 07:50</td>
      <td>2025-01-18 18:58</td>
      <td>35.14</td>
      <td>FILL</td>
      <td>B1</td>
      <td>VialH</td>
      <td>700000 vials</td>
    </tr>
    <tr>
      <td>2025-01-18 18:58</td>
      <td>2025-01-19 18:58</td>
      <td>24.00</td>
      <td>CLEAN</td>
      <td></td>
      <td></td>
      <td>Block reset</td>
    </tr>
    <tr>
      <td>2025-01-19 18:58</td>
      <td>2025-01-19 21:29</td>
      <td>2.51</td>
      <td>FILL</td>
      <td>C3</td>
      <td>VialH</td>
      <td>50000 vials</td>
    </tr>
    <tr>
      <td>2025-01-19 21:29</td>
      <td>2025-01-20 05:29</td>
      <td>8.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialH->VialE</td>
      <td>8h</td>
    </tr>
    <tr>
      <td>2025-01-20 05:29</td>
      <td>2025-01-21 19:08</td>
      <td>37.65</td>
      <td>FILL</td>
      <td>A3</td>
      <td>VialE</td>
      <td>750000 vials</td>
    </tr>
    <tr>
      <td>2025-01-21 19:08</td>
      <td>2025-01-21 23:08</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-21 23:08</td>
      <td>2025-01-22 00:08</td>
      <td>1.00</td>
      <td>FILL</td>
      <td>C1</td>
      <td>VialE</td>
      <td>20000 vials</td>
    </tr>
    <tr>
      <td>2025-01-22 00:08</td>
      <td>2025-01-22 04:08</td>
      <td>4.00</td>
      <td>CHANGEOVER</td>
      <td></td>
      <td>VialE->VialE</td>
      <td>4h</td>
    </tr>
    <tr>
      <td>2025-01-22 04:08</td>
      <td>2025-01-22 09:09</td>
      <td>5.02</td>
      <td>FILL</td>
      <td>A1</td>
      <td>VialE</td>
      <td>100000 vials</td>
    </tr>
  </tbody>
</table>
        </details>
        
</body></html>
