# TrafficVision AI — Exploratory Data Analysis (EDA) Notes

**Prepared by:** Sowjanya Karri (AI/ML — Intern)  
**Team Lead:** Komal Kumari  
**Team number:** 4 
**Dataset:** `traffic_dataset.csv`

---

### What We Looked At

I analysed the traffic dataset provided by the team to understand the structure of the data and identify useful patterns for the TrafficVision AI project. The dataset contains traffic readings with information such as `reading_id`, `road_id`, `sensor_id`, `timestamp`, `vehicle_count`, `avg_speed`, and `density`.

I started by checking the dataset structure, number of records and columns, data types, statistical information, missing values, and duplicate records. I also processed the `timestamp` column and extracted the hour to analyse traffic conditions at different times of the day.

For the initial EDA, I mainly focused on `road_id`, `density`, `vehicle_count`, `avg_speed`, and `hour` as useful traffic-related features.

---

### Key Observations & Traffic Patterns

1. **Traffic Density Distribution:**
   - The distribution of traffic density was analysed using a histogram.
   - This helped in understanding how the density values are distributed across the traffic readings.

2. **Vehicle Count:**
   - Vehicle count was analysed to understand the number of vehicles recorded in different traffic observations.
   - The distribution showed variations in vehicle counts across the dataset.

3. **Average Speed:**
   - Average vehicle speed was analysed to understand the variation in traffic movement.
   - Speed can be useful for understanding traffic conditions along with density and vehicle count.

4. **Road-wise Traffic Density:**
   - Average density was calculated separately for different road IDs.
   - This helped in comparing traffic conditions between different roads.

5. **Time-of-Day Traffic Pattern:**
   - The timestamp was processed and the hour was extracted.
   - Average traffic density was then analysed for different hours of the day.
   - This helped identify how traffic density changes with time.

---

### Data Quality Checks

The dataset was checked for missing values and duplicate records.

- Missing values were checked for all columns.
- Duplicate records were also checked.
- The `timestamp` column was converted into datetime format for further analysis.
- An `hour` feature was created from the timestamp for time-based traffic analysis.

---

### Key Features Identified

Based on the initial analysis, the following features were identified as useful for future congestion prediction:

- **Density** — indicates the level of traffic on a road.
- **Vehicle Count** — represents the number of vehicles detected.
- **Average Speed** — provides information about traffic movement.
- **Time of Day / Hour** — helps identify changes in traffic during different hours.
- **Road ID** — helps compare traffic conditions across different roads.

These features will be useful for the next stages of the AI/ML work, particularly feature preparation and congestion prediction.

---

### Conclusion

The EDA helped me understand the traffic dataset and the main factors that can be useful for congestion prediction. I analysed the traffic density, vehicle count, average speed, road-wise traffic patterns, and time-wise traffic patterns. The identified features will be considered for the upcoming AI/ML development work.

**Day 2 Outcome:**  
Completed the initial traffic dataset exploration and EDA, identified important traffic features, and documented the major observations for further AI/ML development.
