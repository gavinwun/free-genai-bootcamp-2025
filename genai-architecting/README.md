## Functional Requirements

The company wants to invest in owning their infrastructure.
The reason is because there is a concern about the privacy of user data and also a concern that the cost of managed services for GenAI will be greatly raise the cost.

They want to invest in an AI PC where they can afford to spend 10-15K.
They have 300 active students, and students are located within the city of Nagasaki.

## Assumptions

We are assuming that the open-source LLMs that we choose will be powerful enough to run on hardware with an investment of 10-15K.

We're just going to hook up a single server in our office to the internet and we should have enough bandwidth to serve the 300 students.

## Data Strategy

There is a concern of copyrighted materials, so we must purchase and supply materials and store them for access in our database.

## Considerations

We're considering using IBM Granite because it's a truly open-source model with training data that is traceable so we can avoid any copyright issues, and we are able to know what is going on in the model.

https://huggingface.co/ibm-granite

## Monitoring and Optimization

Study activities should have feedback buttons to allow students and instructors to provide feedback of the outputs - e.g. like or dislike, reason for liking or disliking the output.

Feedbacks should be reviewed periodically for prompt improvements and testing as required.

## Governance and Security

A set of policies should be developed on how the LLM should handle inputs and outputs.

Input and output guardrails should inherit from the policies developed to safeguard the LLM data's reponses.

Secure login and audit logs must be implemented for instructors and students access to the platform.

## Scalability and Future-Proofing

Containerization and microservices should be used to implement and maintain the infrastructure and services, so we can scale easily in the future when the business grows and capacity increase is required.
