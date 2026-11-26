EduReach AI

AI/ML-Powered Geospatial Decision Support for Government School Accessibility

<p align="center">
  <a href="https://edureach-ai-aazbtthcnaduqowo5h294t.streamlit.app/">
    <strong>🚀 View Live Application</strong>
  </a>
</p>Study Area: Jamunaha Block, Shravasti, Uttar Pradesh, India
Project Domain: Artificial Intelligence, Machine Learning, Data Analytics and GIS

---

1. Project Overview

EduReach AI is an AI/ML-based geospatial decision-support system designed to analyse government school accessibility at the village level.

The project combines village-level data, school availability indicators, geographic proximity analysis, unsupervised machine learning and interactive visualisation to identify areas that may face gaps in access to government schools.

It aims to support data-informed education infrastructure planning by helping users explore where schools are available, how accessible they may be, and which villages may need further attention.

2. Problem Statement

The presence of a government school in a region does not always mean that every nearby village has convenient access to it.

Some villages may have no recorded local school, while others may have schools but still face geographic accessibility challenges. Looking only at the number of schools can therefore miss important village-level differences.

EduReach AI addresses this problem through a combined analysis of school availability, geographic proximity and school-level indicators.

3. Project Objectives

- Analyse government school accessibility at the village level.
- Identify villages with potential school-accessibility gaps.
- Combine geographic and school-related indicators into an Accessibility Index.
- Apply unsupervised machine learning to explore village-level patterns.
- Present results through an interactive geospatial dashboard.
- Explore hypothetical infrastructure interventions through scenario simulation.

4. Key Features

📍 Geospatial Accessibility Mapping

- Interactive village-level map.
- Geographic representation of school availability and potential accessibility gaps.
- Visual classification based on the Accessibility Index.

📊 Accessibility Index

A composite index is used to assess village-level accessibility through three components:

Component| Weight
School Availability| 40%
Geographic Proximity| 40%
School-Level Coverage| 20%

The resulting score helps compare villages using a common scale.

🤖 Machine Learning-Based Clustering

Gaussian Mixture Model (GMM) is used for unsupervised clustering to explore patterns among villages.

The current implementation uses three descriptive clusters:

- Potential travel/proximity gap or no local school record
- Local school with basic coverage
- Local school with broader coverage

These clusters describe patterns in the available dataset. They are not predictions of educational deprivation.

🔍 Explainability

The dashboard provides village-level analysis to help users understand the factors contributing to an accessibility score.

🧪 Intervention Simulator

The simulator allows users to explore hypothetical changes in accessibility under selected intervention scenarios.

These results are scenario-based estimates, not confirmed outcomes of real infrastructure projects.

5. Dataset and Study Area

The current study focuses on Jamunaha Block, Shravasti, Uttar Pradesh.

The project dataset contains:

- 115 village records
- Geographic coordinates for all 115 villages
- 79 villages with a recorded local school
- 36 villages without a recorded local school

The analysis combines village-level information with school-related indicators and geographic data.

6. Current Analytical Results

Metric| Current Result
Villages Analysed| 115
Villages with Local School Record| 79
Villages without Local School Record| 36
Average Accessibility Index| 67.25
Minimum Index| 0
Maximum Index| 96
Potential Accessibility-Gap Candidates| 36

The dashboard uses the following visual categories:

- Potential Gap: Index below 40
- Moderate: Index from 40 to 70
- Higher: Index above 70

These categories are dashboard classifications, not official government accessibility standards.

7. Technology Stack

Technology| Purpose
Python| Core programming
Pandas| Data processing and analysis
Streamlit| Interactive dashboard
Folium| Geospatial mapping
Streamlit-Folium| Map integration
Scikit-learn| Machine learning
Gaussian Mixture Model| Unsupervised clustering
NumPy| Numerical operations
OpenStreetMap| Geographic map base

8. Project Workflow

1. Collect and prepare village-level and school-related datasets.
2. Clean and integrate relevant data.
3. Process geographic coordinates.
4. Calculate the Accessibility Index using the selected weighted components.
5. Apply GMM-based clustering to explore village patterns.
6. Generate village-level analysis and visual classifications.
7. Display the results through a Streamlit dashboard.
8. Explore hypothetical intervention scenarios.

9. Dashboard Modules

The application includes:

- Overview and KPI cards
- Interactive GIS map
- Village filters and data exploration
- Accessibility analytics
- Machine learning cluster analysis
- Village-level explainability
- Intervention scenario simulator

10. Installation and Local Setup

Follow these steps to run the project locally.

Step 1: Clone the repository

git clone https://github.com/findingtripti/EduReach-AI.git
cd EduReach-AI

Step 2: Install dependencies

pip install -r requirements.txt

Step 3: Run the Streamlit application

streamlit run app.py

The dashboard will open in your browser.

11. SDG Alignment

EduReach AI is aligned with the following United Nations Sustainable Development Goals:

- SDG 4 – Quality Education: Supports analysis of geographic accessibility to government schools.
- SDG 10 – Reduced Inequalities: Helps identify potential differences in school access between villages.
- SDG 9 – Industry, Innovation and Infrastructure: Uses data analytics, GIS and machine learning for infrastructure planning support.

The project is a decision-support prototype and does not claim to have directly achieved these SDG outcomes.

12. Limitations

- The current study is limited to Jamunaha Block, Shravasti.
- Straight-line geographic proximity is used as a distance proxy; actual road distance and travel time may differ.
- A missing local school record does not necessarily prove that a village has no access to a school.
- The Accessibility Index uses selected indicators and assigned weights.
- GMM clusters are descriptive and depend on the selected features and model settings.
- Hypothetical intervention scenarios do not fully account for school capacity, land suitability, implementation costs or other practical constraints.

13. Future Scope

- Extend the analysis to additional blocks and districts.
- Incorporate road-network distance and estimated travel time.
- Include school capacity, infrastructure and student enrolment indicators.
- Improve validation of village-level accessibility estimates.
- Add more detailed intervention planning and cost analysis.
- Integrate updated official datasets as they become available.

14. Project Links

- Live Application: https://edureach-ai-aazbtthcnaduqowo5h294t.streamlit.app/
- GitHub Repository: https://github.com/findingtripti/EduReach-AI

---

Conclusion

EduReach AI brings together geospatial analysis, data analytics and machine learning to explore government school accessibility at the village level. By combining an Accessibility Index, clustering, explainability and scenario simulation, it provides an interactive way to examine potential gaps and support further investigation for education infrastructure planning.

EduReach AI — Making School Accessibility Visible Through Data.
