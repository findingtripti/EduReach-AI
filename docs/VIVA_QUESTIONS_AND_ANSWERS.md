# Viva Questions and Answers

Short, honest answers. Numbers come from the current dataset (115 villages, 79 with a recorded school, 36 without, mean index 67.25).

## Motivation and context

**1. What problem does EduReach AI address?**
A school can be close on a map and still not be practically accessible, and some villages have no recorded local school. The project screens villages for *possible* accessibility gaps so that planners know where to look more closely.

**2. How does it relate to the SDGs?**
It supports SDG 4 (Quality Education), which is about inclusive and equitable access to education. It is a screening aid; it does not prove that any village is deprived.

**3. Why Jamunaha block?**
It is the area for which I could assemble school, village and boundary data. I do not claim it is representative of other blocks.

**4. Who could use it?**
Education planners, researchers and NGOs could use it as a starting point. These are proposed users; it has not been adopted by anyone.

## Data and preprocessing

**5. Where does the data come from?**
School and water-supply reports in Excel and village boundary files (GeoJSON/KML). I still need to confirm the exact publisher, year and download date for each file, so I do not quote them as official sources here.

**6. How did you join villages and schools?**
By lower-cased, trimmed village name. This can fail on spelling differences, so some villages or schools may be mismatched. That is a limitation.

**7. What about missing data?**
Panchayat and JJM fields are empty for 63 villages that did not match the JJM report; I left them empty. The app also checks the main columns and shows an error instead of filling values.

**8. Is the data up to date?**
I do not know. Freshness depends on the source files and has not been confirmed.

**9. Is there a known data error?**
Yes. The primary-school flag used a substring test that also matches "UPS". One village (Dadaura) is affected: coverage 80 instead of 55, index 96 instead of 91. I documented it and did not change the dataset.

## Scoring

**10. How is the index calculated?**
Index = 0.40 x availability + 0.40 x proximity + 0.20 x school-level coverage, on 0-100. Availability is 0 or 100; proximity is 100 x (1 - distance / maximum distance); coverage adds points for primary, upper primary, composite and secondary schools.

**11. Why 40/40/20?**
They are my design choice: presence and nearness matter most, school level matters less. They are not estimated from data, so the index is a project-defined indicator, not a validated metric. A sensitivity analysis is future work.

**12. What are the thresholds?**
Below 40 Potential Gap, 40 to below 70 Moderate, 70 and above Higher. These are project cut-offs, not government categories.

**13. A critical point an examiner may raise: is the index adding information?**
Honestly, in this dataset "Potential Gap" is exactly "no recorded local school": such a village has availability 0 and coverage 0, so its index is below 40, while any village with a school scores at least 80. The index mostly ranks villages within each group. I state this in the dashboard.

## Machine learning

**14. Which model and why?**
A Gaussian Mixture Model with 3 components on 7 standardised features. It is unsupervised because I have no ground-truth labels. I chose it for soft, interpretable groupings.

**15. Supervised vs unsupervised?**
Supervised learning needs labelled outcomes to predict; I have none, so accuracy, precision and recall do not apply. Clustering only describes structure in the features.

**16. Why scale the features?**
Distance (km) and 0/1 flags are on different scales. StandardScaler stops the larger-scale feature dominating.

**17. Why 3 clusters?**
For interpretability. BIC/AIC kept falling up to 5 clusters, but most features are binary and some components hit the covariance floor, so BIC/AIC cannot be trusted to select k. I do not claim 3 is statistically optimal.

**18. How stable are the clusters?**
Refitting with seed 42 reproduces the stored labels exactly. Of five seeds I tested, four give the same grouping and one differs (ARI 0.56).

**19. What do the clusters mean?**
No local school with high travel burden (36), local school with basic coverage (30), local school with broader coverage (49). Because Has_School is an input, the first cluster simply equals the no-school villages. They are descriptive patterns, not predictions of deprivation.

**20. Is the model refitted when I use filters?**
No. Labels are stored and the model is not refitted in the app, so cluster ids keep the same meaning.

## GIS

**21. Which coordinates and distance do you use?**
Each village is the representative point of its polygon in WGS84 (latitude, longitude). Distance is haversine (straight-line).

**22. Why is straight-line distance limited?**
It ignores roads, rivers, terrain, seasons and safety. A school 1 km away across a river may be hard to reach. I have no road-network data, so I label it a proxy everywhere.

**23. Where are the schools?**
At their village's point, not surveyed coordinates. So a village with its own school has distance 0 by construction.

## Explainability and simulation

**24. How do you explain a village's score?**
The panel lists each component's raw score, weight and weighted points and sums them. The sum matches the stored index within rounding (max difference 0.005).

**25. How does the simulator work?**
The user picks an intervention and a percentage. Connectivity improvement closes that share of the proximity gap. The new-school scenario closes that share of the availability and proximity gaps and keeps coverage constant. The index change uses the same weights. The data file is never changed.

**26. Are the simulator results predictions?**
No. They are the arithmetic of assumptions. A new school's capacity, staffing, land, cost and feasibility are not modelled. A 100% assumption is deliberately extreme.

## Evaluation, ethics, future

**27. How did you evaluate it?**
Automated tests for formulas, thresholds, reproducibility, scenarios, filters and the map, plus opening the dashboard in a browser. There is no field validation, and I cannot claim the results match reality.

**28. What are the ethical concerns?**
Labels like "Potential Gap" can stigmatise places or drive wrong decisions if over-read. The tool should prompt local verification, not decide funding. Only public, village-level data are used.

**29. What would you improve first?**
Road-network travel time, surveyed school coordinates, enrolment evidence, sensitivity analysis of the weights, fixing the primary/upper-primary flag, and field checks.

**30. What do you say if asked "so what did the AI add?"**
A transparent score, a reproducible grouping of villages with an honest account of its limits, and a way to explore assumptions. The strongest result is not a prediction but a clear, checkable shortlist of 36 villages without a recorded local school.
