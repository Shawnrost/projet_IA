from rest_framework import serializers


class ChurnPredictionInputSerializer(serializers.Serializer):

    gender = serializers.ChoiceField(choices=["Male", "Female"])
    SeniorCitizen = serializers.ChoiceField(choices=[0, 1])
    Partner = serializers.ChoiceField(choices=["Yes", "No"])
    Dependents = serializers.ChoiceField(choices=["Yes", "No"])
    tenure = serializers.IntegerField(min_value=0)
    PhoneService = serializers.ChoiceField(choices=["Yes", "No"])
    MultipleLines = serializers.ChoiceField(
        choices=["Yes", "No", "No phone service"]
    )
    InternetService = serializers.ChoiceField(
        choices=["DSL", "Fiber optic", "No"]
    )
    OnlineSecurity = serializers.ChoiceField(
        choices=["Yes", "No", "No internet service"]
    )
    OnlineBackup = serializers.ChoiceField(
        choices=["Yes", "No", "No internet service"]
    )
    DeviceProtection = serializers.ChoiceField(
        choices=["Yes", "No", "No internet service"]
    )
    TechSupport = serializers.ChoiceField(
        choices=["Yes", "No", "No internet service"]
    )
    StreamingTV = serializers.ChoiceField(
        choices=["Yes", "No", "No internet service"]
    )
    StreamingMovies = serializers.ChoiceField(
        choices=["Yes", "No", "No internet service"]
    )
    Contract = serializers.ChoiceField(
        choices=["Month-to-month", "One year", "Two year"]
    )
    PaperlessBilling = serializers.ChoiceField(choices=["Yes", "No"])
    PaymentMethod = serializers.ChoiceField(
        choices=[
            "Electronic check",
            "Mailed check",
            "Bank transfer (automatic)",
            "Credit card (automatic)",
        ]
    )
    MonthlyCharges = serializers.FloatField(min_value=0)
    TotalCharges = serializers.FloatField(min_value=0)


class ChurnPredictionOutputSerializer(serializers.Serializer):
    churn_prediction = serializers.ChoiceField(choices=["Yes", "No"])
    churn_probability = serializers.FloatField()