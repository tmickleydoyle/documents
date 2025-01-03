# Monstera: Company Metric Design

### Introduction

Monstera is a project designed to build a robust ecosystem of metrics that explain how entities interact with products and features. These metrics are anchored in the core events that drive engagement on the platform, allowing for a granular view of the company’s operations. The metric structure follows an event tree hierarchy, enabling teams across product, operations, and engineering to zoom in and out—whether they need to observe overarching trends or focus on specific entity actions over varying timeframes.

The framework promotes a structured, disciplined approach to understanding business performance. By standardizing key events, every team is encouraged to think of their role in the company as a lever that influences the flow of entities and their actions through various aspects of the organization. Engineering teams are responsible for implementing specific entity events and ensuring the accuracy of the data sent to the pipeline. The data team ensures all data is properly gathered and adheres to set standards. Meanwhile, product and operations teams are tasked with maintaining the business logic, ensuring that the data reflects accurate and actionable insights for decision-making. Leadership will continuously track these metrics against company goals and objectives, providing a clear view of how different functions contribute to overall success.

Moreover, this structured approach extends beyond just metrics—it is reflected in the design of the dashboards used by the teams. The dashboards follow a similar tree structure, allowing users to start at high-level company metrics and drill down to more granular, event-level data. This seamless movement between layers ensures that teams can quickly identify trends and diagnose issues. All dashboards will be certified by the data team, ensuring accuracy and consistency across the organization.

To guarantee reliability, all events will adhere to a transactional structure. These events will capture relevant information about the entity, the type of entity, the action taken, and the location where the event occurred. This core object model standardizes data collection, ensuring that all critical attributes are captured consistently, which not only aids in analysis but also ensures that decisions are based on comprehensive and reliable data.

This opinionated approach to metric design avoids the pitfalls of disjointed metrics developed independently by different teams, which can fragment focus and dilute the company’s resources. Historically, businesses that have failed to maintain a unified metric strategy have suffered from slow growth and missed opportunities to truly understand their operational dynamics. By focusing on a structured metric and dashboard design, Monstera ensures that the company maintains its focus, fostering both scalability and deep insights into the way the business operates.

### Metrics as the Cornerstone of Decision-Making
 Metrics are the foundation upon which informed decision-making is built. For metrics to be a reliable asset in any organization, they must be developed in a stable and trustworthy manner. Inconsistent or loosely defined metrics can undermine confidence at every level—from senior leadership down to the individuals responsible for creating events and maintaining business logic. A lack of standardized and robust metrics not only leads to unreliable forecasting but also hinders the ability to set and achieve meaningful monthly or quarterly goals.

One of the key challenges that organizations face when developing metrics is “metric drift”—the slow evolution of metric definitions as different teams interpret business logic in various ways. Without centralized definitions, teams may inadvertently deviate from the original intent of a metric, resulting in inconsistent data that lacks clarity and alignment. This fragmentation makes it difficult to identify the “golden data”—the most valuable, standardized data that drives key decisions around adoption, retention, and performance improvement. Establishing and maintaining a rigorous, standardized approach to metric development is essential for avoiding this drift.

Once metrics are standardized, they enhance the company's ability to perform ad hoc analysis with greater efficiency and accuracy. Clean, well-defined data allows for the identification of patterns and trends, enabling stakeholders across the company to make faster, more informed decisions. Self-service analytics becomes significantly easier as the data takes on a consistent shape, with clear definitions, lineage, and documentation that reduce the barriers to independent exploration. Teams can dive into the data without the need for constant guidance from the data team, fostering a more data-driven culture across the organization.

In addition to easing ad hoc analysis, standardized metrics are critical in enabling reliable alerting systems. When rules behind alerts are well-documented and consistently applied, stakeholders are better equipped to understand and react to anomalies in the data. If an alert fires, everyone understands the logic behind it, making it easier to diagnose issues and determine whether the anomaly is due to external factors or internal system changes. This responsiveness to anomalies helps in maintaining operational integrity and avoiding missed opportunities or unchecked risks.

Moreover, standardized metrics and clean data significantly streamline more advanced analytical processes. Operations such as descriptive statistics, hypothesis testing, correlation analysis, and time series analysis all depend on the quality and consistency of the underlying data. Without trustworthy metrics, these operations become less reliable, as the noise from inconsistent or poorly defined data obscures meaningful insights. A disciplined approach to metric design ensures that these statistical and analytical methods can be applied with confidence, yielding actionable insights that drive business growth and operational efficiency.

By developing metrics that are reliable, well-documented, and consistent across the company, Monstera creates a robust foundation for both everyday decision-making and long-term strategic planning. These metrics provide the clarity needed to understand performance, identify opportunities, and react effectively to challenges, ensuring that the entire organization is aligned and moving in the right direction.

### Implementation: Turning Philosophy into Action

**1. Surveying the Data Landscape**  
Before any code is written or data is moved, it is crucial to first conduct a comprehensive survey of the data landscape. This involves mapping out how entities (such as users, accounts, videos, or projects) interact with products and features, and understanding the relationships between these interactions. For instance, consider the workflow where a user signs up for an account, creates a video project, adds comments to different parts of the video, and publishes it. Each of these actions follows a specific order, and mapping this sequence helps define how the metrics will be structured.

Key points in this phase include:
- **Identify unique vs. repeatable events**: Some events, like account creation, happen once, while others, like adding videos or comments, may occur multiple times. Recognizing this distinction ensures that the metrics capture the correct frequency of actions, and helps with setting up alerts to track the different types of events.
- **Map event dependencies**: Understanding the flow of actions (e.g., publishing a video can only happen after it has been created and edited) ensures that workflows are correctly mapped. This hierarchical view will become the foundation of the event tree used in metrics.
- **Explore workflow boundaries**: Not all interactions need to be mapped at once, but key workflows should be defined early to ensure that critical actions are captured. As new workflows emerge, they should be carefully integrated to allow for controlled experiments like A/B testing or other ad hoc analysis.

By fully understanding the flow of interactions, we can begin to frame the data model that will be used to generate reliable and accurate metrics.

**2. Designing Event Trees and Metrics**  
Once the data landscape is well understood, the next step is to design the event trees that will feed into the metrics. Event trees represent how various entity interactions can be grouped into meaningful sequences, forming the backbone of the metric system.

- **Create a hierarchy of events**: Start by defining the top-level events that represent major user actions (e.g., signing up, uploading a video, publishing content). Beneath each top-level event, smaller sub-events may occur (e.g., within the process of uploading a video, there could be stages like adding a title, uploading the file, and saving the draft).
- **Define standard metrics for each workflow**: With the event trees in place, metrics can be created to measure the performance of each key event. These metrics could include user engagement rates (e.g., how many users progress through all steps of video creation), retention rates, and frequency of specific actions. 
- **Iterative approach to metric creation**: While the entire company doesn’t need to be mapped out initially, complete workflows for critical processes must be defined to avoid gaps in data. As new workflows or product features are introduced, the event trees can be expanded or refined accordingly.

**3. Building Standardized Data Models**  
With the event trees and entity workflows established, the next step is to develop standardized data models that centralize and organize data in a way that enables clean, consistent metric calculations. These models serve as the foundation for how data is stored, accessed, and transformed into actionable insights.

- **Create action-focused tables**: Centralize all actions or activities that entities perform into "action tables." These tables should consolidate data from various sources but maintain a focus on the specific activities taken by entities within defined families. For example, all actions taken in the video creation and update workflow should be grouped together. User signup and member invitations should be in a separate flow.
  
- **Entity vs. activity tables**: To maintain clarity and separation of concerns, create two types of tables:
  - **Activity/action tables**: Capture all interactions and activities performed by entities, such as logging in, uploading videos, or posting comments. These tables organize actions in a structured and chronological manner. Transactional data preferred.
  - **Entity tables**: Store the descriptive data related to entities themselves (e.g., user profiles, account details, video metadata). These tables reflect the latest state of each entity, allowing for easy enrichment of the action tables when performing analysis. CDC or similar tables structure preferred.

**4. Building Metrics Values**  
Once the data models are in place, the final step is to calculate the metrics themselves. The calculation of metrics can vary based on the company’s data infrastructure, and there are multiple approaches to choose from, depending on the level of complexity and the desired responsiveness of the system.

- **Enriching action data with entity data**: At this stage, it is crucial to join the action tables back with the entity tables. This step allows for segmenting the overall metrics into more granular metrics based on key attributes of the entities. For example, instead of just tracking general activity metrics (like login frequency or video uploads), we can create more specific metrics by segmenting the data. Some examples include:
  - **Frequency by country**: Using the entity data (e.g., user profiles or account information), actions can be segmented by location to analyze regional performance trends.
  - **Metrics by account age**: Segmenting metrics based on how long a user has had an account (e.g., new users versus long-time users) can offer insights into engagement or retention.
  - **Other demographic or entity-based segments**: Depending on the available attributes in the entity tables, further segmentation can be applied (e.g., industry, role, account type, or other key identifiers).

  By enriching the action data with relevant entity information, the company can create tailored views of performance for different segments, making it easier to understand how certain entity characteristics affect the metrics.

- **Cube-based approach**: One method for calculating metrics is to structure the data into a multi-dimensional cube, allowing for dynamic calculations at query time. This approach offers flexibility and allows users to quickly slice and dice data based on different entity segments (e.g., country, age group, etc.). However, dynamic calculations may require significant computational resources and may affect query performance as the volume of data grows.

- **Pre-computed metrics**: In cases where performance is a concern, metrics can be pre-aggregated and stored in summary tables. This method allows for faster queries since metrics are calculated ahead of time, but the trade-off is that the data may not reflect the most recent activities. Even in a pre-computed approach, it’s important to ensure that action data is correctly enriched with entity data to enable segmented views of the metrics.

- **Hybrid approaches**: Depending on the specific needs and technical infrastructure, a combination of cube-based and pre-computed metrics can be used. For example, high-frequency metrics like daily login counts can be calculated dynamically, while more stable metrics like monthly active users or long-term retention rates can be pre-computed and segmented by various entity attributes.

By joining action and entity tables, metrics become far more versatile and informative. Segmenting metrics based on entity characteristics allows for deeper insights, which is essential for understanding different user behaviors, trends, and key performance drivers across various segments of the business. This step is a critical part of transforming raw data into actionable insights that drive more granular and targeted decision-making.

### Dashboard Design: Structuring Metrics for Actionable Insights

A well-designed dashboard is essential for conveying metrics in a clear and actionable way. The goal of the Monstera dashboard design is to provide a structured, intuitive view of the company’s key metrics while maintaining consistency and clarity across all dashboards. To achieve this, dashboards will follow a **tree structure**, with **three types of dashboards**—Overall View, Segment View, and Activity View—each rolling up into the next. This approach ensures users can easily navigate from detailed activity metrics all the way up to high-level company performance, without losing context.

**1. Dashboard Types and Tree Structure**
The three dashboard types follow a hierarchical structure, allowing users to zoom in and out based on their level of analysis.

- **Overall View Dashboards**:  
  These are the top-level dashboards that provide a holistic view of the company’s most important metrics. Designed for leadership and strategic decision-making, these dashboards include big number tiles to highlight the current state of key metrics such as total active users, revenue, or retention rates. Additionally, line or bar chart can be found here, but they will only include the last 90-days of data. Users will also be able to drill down from the Overall View into Segment or Activity View dashboards for a more detailed analysis.
  
  **Example**: The overall dashboard might include metrics like “Monthly Active Users” or “Total Revenue,” each represented with big number tiles alongside line and bar charts that show trends over time.

- **Segment View Dashboards**:  
  The Segment View dashboards focus on breaking down the overall metrics by key entity segments, such as geography, account type, or product usage. These dashboards allow users to understand how different segments contribute to the overall performance and identify trends or anomalies in specific groups. Line and bar charts will include up to 18-months of data.
  
  **Example**: A Segment View dashboard might include a chart for “Monthly Active Users by Country” or “Revenue by Account Age,” allowing teams to explore how different segments of the user base behave.

- **Activity View Dashboards**:  
  The Activity View dashboards are the most granular level, focusing on specific actions or workflows taken by entities. These dashboards show how users interact with the platform in detail, such as the number of videos uploaded, the average time spent on specific features, or the frequency of comments on videos. Activity metrics roll up into Segment Views, providing insights into how actions differ across various segments. Line and bar charts will include up to 18-months of data.
  
  **Example**: An Activity View dashboard might track “Video Uploads by Day” or “Comments Added to Videos per User,” giving teams detailed information about user behavior at a granular level.

**2. Standardized Dashboard Design and Naming Conventions**
To maintain clarity and consistency, all dashboards will adhere to a **standard design** and **naming patterns** for charts and visual elements. This ensures that users can easily interpret the data without needing assistance from the data team.

- **Design Standards**:
  - **Allowed Chart Types**: Only three chart types are permitted for metrics dashboards:
    1. **Bar charts**: For comparing discrete values, such as the number of users across different segments.
    2. **Line charts**: For tracking changes over time, such as daily active users over the past month.
    3. **Big number tiles**: To display current metric values, especially in Overall View dashboards, to highlight critical KPIs (e.g., total users, monthly revenue).
  
  This limited selection of chart types ensures simplicity and uniformity, making it easier for users to understand the data at a glance.

- **Naming Conventions for Charts**:  
  The naming of charts will follow a consistent pattern to provide users with clear information about what is being measured. The format for chart names will be:

```
[Entities], [Metric], [Timeframe], [by Segment or Event] (if applicable)
```

  - **Entity**: Refers to the subject of the metric (e.g., "Signups," "New Videos").
  - **Metric**: Describes the key performance indicator (e.g., "Weekly Active," "Monthly").
  - **Timeframe**: Specifies the time period for the metric (e.g., "Current," "Last 90 Days").
  - **by Segment or Event** (optional): Indicates that the data is segmented or related to specific events (e.g., "by Country," "by Account Age").

**Example**:  
- "New Videos, Weekly Active, Last 90 Days by Country" (Segment View)  
- "New Videos, Weekly Active, Last 90 Days by Status" (Activity View)  
- "New Videos, Weekly Active, Last 90 Days" (Overall View)

**3. Recording Metrics in the Data Catalog**
All metrics included in the dashboards will be documented in a **data catalog**. This catalog serves as a central resource where users can look up detailed information on how each metric is calculated, what the naming conventions mean, and how the charts are organized. This transparency helps users understand the data at a deeper level and ensures that everyone is working with the same definitions, reducing confusion or misinterpretation.

The data catalog will also provide links to the relevant dashboards, making it easy for users to discover and navigate between them. It is crucial that every metric in the system has a corresponding entry in the catalog, including details on its data sources, calculation methods, and how it ties into the overall metric framework.

**4. Linking Dashboards for Seamless Discovery**
To make it easier for users to explore data across different levels of detail, all child dashboards will include links back to their parent dashboards. This ensures seamless movement between different layers of analysis—users can start with high-level metrics and drill down into segment or activity-specific views with a single click, and vice versa. This interconnected structure promotes intuitive data exploration and reduces the need for manual searches.

Additionally, all dashboard names will follow a consistent format to provide immediate clarity about what users are viewing. The naming format for dashboards will be:

```
[Level]: [Metric]
```

**Example**:  
- "Overall: Signups"
- "Segment: Signups
- "Activity: Signups”

This standard naming system provides a clear understanding of the dashboard's focus and hierarchy, improving navigation and reducing ambiguity.

**5. “Land, Learn, and Leave” Design Principle**
The overall design philosophy behind the dashboards is for users to "land, learn, and leave." The goal is to provide a self-service environment where users can quickly access the data they need, understand it without external assistance, and make informed decisions before moving on to other tasks. This principle is supported by:
- **Clear naming conventions** that allow users to immediately know what they are viewing.
- **Consistent design** across all dashboards, reducing the learning curve.
- **Self-explanatory metrics and chart types** that avoid unnecessary complexity.

By following these principles, users should be able to interpret the results of their data exploration without needing to involve the data team for clarification.

**6. Other Dashboards Outside of Metrics**
While the metrics dashboards are owned and maintained by the data team to ensure consistency and reliability, other dashboards can be created outside of this framework. These dashboards might focus on specific team needs, projects, or ad hoc analyses, and do not have to follow the strict design guidelines laid out for metrics dashboards. However, they will remain separate from the core metrics dashboards and may not be certified by the data team.
