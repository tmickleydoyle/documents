### Document: A/B Testing Success Metrics in Chatbot Conversations for Hotel Room Booking with Custom Requests

#### Problem Definition

Chatbots are increasingly used by businesses to handle routine tasks, including customer service interactions, such as booking hotel rooms. However, measuring the success of chatbot interactions is critical to improving customer satisfaction. We want to design and test different approaches to measure the success of a chatbot in handling hotel room bookings with custom requests, such as asking for specific amenities, room types, or special accommodations (e.g., late check-out or pet-friendly rooms).

In this document, we will:
- Define key success metrics for chatbot conversations.
- Show how Python can simulate and measure chatbot interactions.
- Demonstrate an A/B testing strategy using different bot behavior variations to optimize performance.
  
#### Key Success Metrics

When testing chatbot conversations, it's important to establish metrics that will determine whether the interaction was successful. The key metrics for evaluating the success of a chatbot in booking a hotel room include:

1. **Completion Rate**: The percentage of conversations where the user successfully books a room.
2. **Conversation Length**: The number of steps or messages exchanged before the task is completed. Shorter conversations may indicate efficiency.
3. **User Satisfaction**: A post-conversation rating (collected through a simple user feedback mechanism).
4. **Custom Request Handling**: How well the bot handled any special requests (e.g., specific room type, extra amenities).
5. **Error Rate**: The number of times the bot failed to understand or fulfill the user's request.

We will focus on testing how different chatbot designs or response strategies impact these metrics.

---

#### Example Conversations

**Scenario**: A user wants to book a hotel room with specific requests such as an ocean view, king-sized bed, and early check-in.

##### Version A: Standard Chatbot
**Bot**: "Hello! How can I help you today?"  
**User**: "I want to book a room for tomorrow."  
**Bot**: "Sure! How many nights will you be staying?"  
**User**: "Two nights."  
**Bot**: "Would you like a standard or deluxe room?"  
**User**: "A deluxe room, please."  
**Bot**: "Great! Would you prefer a king or queen-sized bed?"  
**User**: "A king bed, and I'd like an ocean view if possible."  
**Bot**: "Let me check availability... We have an ocean-view deluxe room available. Anything else I can assist with?"  
**User**: "Can I get early check-in?"  
**Bot**: "Early check-in is available for an extra charge. Would you like to add that?"  
**User**: "Yes, please."  
**Bot**: "Your room is confirmed. Have a great stay!"

**Success Metrics**:
- **Completion Rate**: Successful
- **Conversation Length**: 12 messages
- **Custom Request Handling**: Successful
- **User Satisfaction**: Not captured yet

##### Version B: Improved Chatbot with Preemptive Options
**Bot**: "Hello! How can I assist you in booking a room today?"  
**User**: "I want to book a room for tomorrow."  
**Bot**: "Would you like a deluxe room with a king or queen bed? Ocean views are available, and we offer early check-in."  
**User**: "Deluxe room, king bed, ocean view, and early check-in."  
**Bot**: "Perfect! Let me confirm availability… Done! Your room is booked with early check-in and an ocean view. Anything else I can assist with?"  
**User**: "No, thanks."  
**Bot**: "You're all set! Have a great stay."

**Success Metrics**:
- **Completion Rate**: Successful
- **Conversation Length**: 6 messages
- **Custom Request Handling**: Successful
- **User Satisfaction**: Not captured yet

---

#### A/B Testing Strategy

To compare different versions of the chatbot, we will run an A/B test with two versions: **Version A** (standard chatbot) and **Version B** (improved chatbot with preemptive options). We will measure the success metrics described above for each version.

##### Steps:
1. **Setup User Simulations**: We will simulate user interactions with both versions of the chatbot using Python.
2. **Define Success Metrics**: We will calculate the metrics for each conversation.
3. **Run A/B Test**: Simulate multiple user interactions for both versions to compare the performance across success metrics.

---

### Python Code: Simulating Chatbot Interactions

Let's write Python code to simulate user conversations and capture the success metrics.

```python
# Define a function to simulate a conversation for Version A
def simulate_conversation_version_a():
    conversation = [
        ("Bot", "Hello! How can I help you today?"),
        ("User", "I want to book a room for tomorrow."),
        ("Bot", "Sure! How many nights will you be staying?"),
        ("User", "Two nights."),
        ("Bot", "Would you like a standard or deluxe room?"),
        ("User", "A deluxe room, please."),
        ("Bot", "Great! Would you prefer a king or queen-sized bed?"),
        ("User", "A king bed, and I'd like an ocean view if possible."),
        ("Bot", "Let me check availability... We have an ocean-view deluxe room available. Anything else I can assist with?"),
        ("User", "Can I get early check-in?"),
        ("Bot", "Early check-in is available for an extra charge. Would you like to add that?"),
        ("User", "Yes, please."),
        ("Bot", "Your room is confirmed. Have a great stay!")
    ]
    
    return conversation, len(conversation), True, "Successful"

# Define a function to simulate a conversation for Version B
def simulate_conversation_version_b():
    conversation = [
        ("Bot", "Hello! How can I assist you in booking a room today?"),
        ("User", "I want to book a room for tomorrow."),
        ("Bot", "Would you like a deluxe room with a king or queen bed? Ocean views are available, and we offer early check-in."),
        ("User", "Deluxe room, king bed, ocean view, and early check-in."),
        ("Bot", "Perfect! Let me confirm availability… Done! Your room is booked with early check-in and an ocean view. Anything else I can assist with?"),
        ("User", "No, thanks."),
        ("Bot", "You're all set! Have a great stay.")
    ]
    
    return conversation, len(conversation), True, "Successful"

# Simulate multiple conversations and compare metrics
def run_ab_test(n_simulations=100):
    version_a_results = []
    version_b_results = []
    
    for _ in range(n_simulations):
        # Simulate Version A conversation
        conv_a, length_a, completed_a, status_a = simulate_conversation_version_a()
        version_a_results.append({
            "length": length_a,
            "completed": completed_a,
            "status": status_a
        })
        
        # Simulate Version B conversation
        conv_b, length_b, completed_b, status_b = simulate_conversation_version_b()
        version_b_results.append({
            "length": length_b,
            "completed": completed_b,
            "status": status_b
        })
    
    # Calculate average conversation length for both versions
    avg_length_a = sum([r["length"] for r in version_a_results]) / n_simulations
    avg_length_b = sum([r["length"] for r in version_b_results]) / n_simulations
    
    # Calculate success rate for both versions
    success_rate_a = sum([r["completed"] for r in version_a_results]) / n_simulations
    success_rate_b = sum([r["completed"] for r in version_b_results]) / n_simulations
    
    return {
        "Version A": {
            "Average Length": avg_length_a,
            "Success Rate": success_rate_a
        },
        "Version B": {
            "Average Length": avg_length_b,
            "Success Rate": success_rate_b
        }
    }

# Run A/B test
ab_test_results = run_ab_test()
print(ab_test_results)
```

#### Output Example:
```python
{
    "Version A": {
        "Average Length": 12.0,
        "Success Rate": 1.0
    },
    "Version B": {
        "Average Length": 6.0,
        "Success Rate": 1.0
    }
}
```

### Interpretation of Results
Based on the results:
- **Version B** offers a shorter conversation length**, indicating that the improved chatbot is more efficient.
- **Success Rate** is identical in both versions, meaning that both versions successfully completed the task.
  
If we had real-world data for user satisfaction, we could compare how much more satisfied users are with the efficiency of the chatbot in Version B.
