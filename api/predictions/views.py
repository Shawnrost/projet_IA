import os
import joblib
import pandas as pd
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    ChurnPredictionInputSerializer,
    ChurnPredictionOutputSerializer,
)


MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "model_output")

model = joblib.load(os.path.join(MODEL_DIR, "model.pkl"))
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
encoders = joblib.load(os.path.join(MODEL_DIR, "encoders.pkl"))
feature_order = joblib.load(os.path.join(MODEL_DIR, "feature_order.pkl"))


class ChurnPredictionView(APIView):
    

    def post(self, request):
        input_serializer = ChurnPredictionInputSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)
        data = input_serializer.validated_data

        
        row = {}
        for col in feature_order:
            value = data[col]
            if col in encoders:
                
                value = encoders[col].transform([value])[0]
            row[col] = value

        df_input = pd.DataFrame([row], columns=feature_order)
        df_input_scaled = scaler.transform(df_input)

        prediction = model.predict(df_input_scaled)[0]
        probability = model.predict_proba(df_input_scaled)[0][1]

        result = {
            "churn_prediction": "Yes" if prediction == 1 else "No",
            "churn_probability": round(float(probability), 4),
        }

        output_serializer = ChurnPredictionOutputSerializer(result)
        return Response(output_serializer.data, status=status.HTTP_200_OK)