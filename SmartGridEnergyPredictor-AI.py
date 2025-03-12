import json
import csv
import re
from datetime import datetime
import math

class SmartGridEnergyPredictor:
    def __init__(self):
        self.records = []
        self.validation_errors = []
        self.validation_summary = {
            "total_records": 0,
            "fields_status": {
                "timestamp": "missing",
                "historical_energy_consumption": "invalid",
                "parameter_a": "invalid",
                "parameter_b": "invalid",
                "forecast_time": "invalid",
                "baseline": "invalid"
            }
        }
    
    def validate_iso_timestamp(self, timestamp, row_num):
        """Validate if the timestamp is in ISO format"""
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError):
            self.validation_errors.append(f"ERROR: Invalid timestamp format in row {row_num}. Expected ISO format.")
            return False

    def validate_positive_number(self, value, field_name, row_num):
        """Validate if the value is a positive number"""
        try:
            num_value = float(value)
            if num_value <= 0:
                self.validation_errors.append(f"ERROR: Invalid value for field '{field_name}' in row {row_num}. Expected positive number.")
                return False
            return True
        except (ValueError, TypeError):
            self.validation_errors.append(f"ERROR: Invalid value for field '{field_name}' in row {row_num}. Expected numeric value.")
            return False

    def validate_positive_integer(self, value, field_name, row_num):
        """Validate if the value is a positive integer"""
        try:
            int_value = int(float(value))
            if int_value <= 0 or int_value != float(value):
                self.validation_errors.append(f"ERROR: Invalid value for field '{field_name}' in row {row_num}. Expected positive integer.")
                return False
            return True
        except (ValueError, TypeError):
            self.validation_errors.append(f"ERROR: Invalid value for field '{field_name}' in row {row_num}. Expected integer value.")
            return False

    def validate_record(self, record, row_num):
        """Validate a single record"""
        valid_record = True
        
        # Check for missing fields
        required_fields = ["timestamp", "historical_energy_consumption", "parameter_a", 
                          "parameter_b", "forecast_time", "baseline"]
        
        missing_fields = [field for field in required_fields if field not in record or not record[field]]
        
        if missing_fields:
            self.validation_errors.append(f"ERROR: Missing required field(s): {', '.join(missing_fields)} in row {row_num}.")
            valid_record = False
        
        # Validate individual fields if they exist
        if "timestamp" in record and record["timestamp"]:
            if self.validate_iso_timestamp(record["timestamp"], row_num):
                self.validation_summary["fields_status"]["timestamp"] = "present"
        
        if "historical_energy_consumption" in record and record["historical_energy_consumption"]:
            if self.validate_positive_number(record["historical_energy_consumption"], "historical_energy_consumption", row_num):
                self.validation_summary["fields_status"]["historical_energy_consumption"] = "valid"
        
        if "parameter_a" in record and record["parameter_a"]:
            if self.validate_positive_number(record["parameter_a"], "parameter_a", row_num):
                self.validation_summary["fields_status"]["parameter_a"] = "valid"
        
        if "parameter_b" in record and record["parameter_b"]:
            if self.validate_positive_number(record["parameter_b"], "parameter_b", row_num):
                self.validation_summary["fields_status"]["parameter_b"] = "valid"
        
        if "forecast_time" in record and record["forecast_time"]:
            if self.validate_positive_integer(record["forecast_time"], "forecast_time", row_num):
                self.validation_summary["fields_status"]["forecast_time"] = "valid"
        
        if "baseline" in record and record["baseline"]:
            if self.validate_positive_number(record["baseline"], "baseline", row_num):
                self.validation_summary["fields_status"]["baseline"] = "valid"
        
        return valid_record

    def parse_csv_data(self, csv_data):
        """Parse CSV data and return records"""
        try:
            lines = csv_data.strip().split('\n')
            reader = csv.DictReader(lines)
            records = list(reader)
            return records
        except Exception as e:
            self.validation_errors.append(f"ERROR: Invalid CSV format. {str(e)}")
            return []

    def parse_json_data(self, json_data):
        """Parse JSON data and return records"""
        try:
            data = json.loads(json_data)
            if "records" in data and isinstance(data["records"], list):
                return data["records"]
            else:
                self.validation_errors.append("ERROR: Invalid JSON format. Expected 'records' array.")
                return []
        except json.JSONDecodeError as e:
            self.validation_errors.append(f"ERROR: Invalid JSON format. {str(e)}")
            return []

    def detect_and_parse_data(self, data):
        """Detect data format and parse accordingly"""
        data = data.strip()
        
        # Try to determine if it's CSV or JSON
        if data.startswith("{"):
            return self.parse_json_data(data)
        elif "," in data and ("\n" in data or len(data.split(",")) >= 6):
            return self.parse_csv_data(data)
        else:
            self.validation_errors.append("ERROR: Invalid data format. Please provide data in CSV or JSON format.")
            return []

    def validate_data(self, data):
        """Validate the provided data"""
        self.validation_errors = []
        self.records = []
        
        parsed_records = self.detect_and_parse_data(data)
        self.validation_summary["total_records"] = len(parsed_records)
        
        valid_records = []
        for i, record in enumerate(parsed_records, 1):
            if self.validate_record(record, i):
                # Convert numeric strings to actual numbers
                processed_record = {
                    "timestamp": record["timestamp"],
                    "historical_energy_consumption": float(record["historical_energy_consumption"]),
                    "parameter_a": float(record["parameter_a"]),
                    "parameter_b": float(record["parameter_b"]),
                    "forecast_time": int(float(record["forecast_time"])),
                    "baseline": float(record["baseline"])
                }
                valid_records.append(processed_record)
        
        self.records = valid_records
        return len(self.validation_errors) == 0

    def generate_validation_report(self):
        """Generate the data validation report"""
        report = "# Smart Grid Data Validation Report:\n"
        report += f"- Total Records Evaluated: {self.validation_summary['total_records']}\n"
        report += "## Required Fields Check:\n"
        
        for field, status in self.validation_summary["fields_status"].items():
            report += f"   - {field}: {status}\n"
        
        report += "\n# Validation Summary:\n"
        if not self.validation_errors:
            report += "Data validation is successful! Would you like to proceed with the forecast analysis or provide another dataset?\n"
        else:
            for error in self.validation_errors:
                report += f"- {error}\n"
        
        return report

    def calculate_predictions(self):
        """Calculate predictions for each record"""
        results = []
        
        for record in self.records:
            # Step 1: Adjusted Consumption Calculation
            adjusted_consumption = record["historical_energy_consumption"] * record["parameter_a"]
            
            # Step 2: Time Adjustment Calculation
            time_adjustment = record["parameter_b"] * record["forecast_time"]
            
            # Step 3: Predicted Energy Consumption Calculation
            predicted_energy = record["baseline"] + adjusted_consumption + time_adjustment
            
            # Step 4: Relative Error Calculation
            relative_error = abs((predicted_energy - record["historical_energy_consumption"]) / 
                                record["historical_energy_consumption"]) * 100
            
            # Step 5: Forecast Confidence Score Calculation
            confidence_score = 100 - relative_error
            
            # Determine reliability status
            if relative_error <= 10 and confidence_score >= 90:
                status = "Highly Reliable"
                recommendation = "Forecast is highly reliable."
            elif (relative_error > 10 and relative_error <= 20) or (confidence_score >= 80 and confidence_score < 90):
                status = "Moderately Reliable"
                recommendation = "Forecast is moderately reliable."
            else:  # relative_error > 20 or confidence_score < 80
                status = "Low Reliability"
                recommendation = "Forecast reliability is low. Further analysis is required."
            
            results.append({
                "record": record,
                "adjusted_consumption": round(adjusted_consumption, 2),
                "time_adjustment": round(time_adjustment, 2),
                "predicted_energy": round(predicted_energy, 2),
                "relative_error": round(relative_error, 2),
                "confidence_score": round(confidence_score, 2),
                "status": status,
                "recommendation": recommendation
            })
        
        return results

    def generate_forecast_report(self, results):
        """Generate detailed forecast report"""
        report = "# Smart Grid Energy Consumption Forecast Summary\n\n"
        report += f"**Total Records Evaluated:** {len(results)}\n\n"
        report += "---\n\n"
        
        for result in results:
            record = result["record"]
            report += f"## Detailed Analysis per Record\n\n"
            report += f"**Record Identifier:** {record['timestamp']}\n\n"
            
            report += "### Input Data\n"
            report += f"- **Historical Energy Consumption:** {record['historical_energy_consumption']}\n"
            report += f"- **Parameter A:** {record['parameter_a']}\n"
            report += f"- **Parameter B:** {record['parameter_b']}\n"
            report += f"- **Forecast Time (hours):** {record['forecast_time']}\n"
            report += f"- **Baseline Consumption:** {record['baseline']}\n\n"
            
            report += "---\n\n"
            report += "## Detailed Calculations\n\n"
            
            report += "### 1. Adjusted Consumption Calculation\n"
            report += "- **Formula:** $$ \\text{Adjusted Consumption} = \\text{historical_energy_consumption} \\times \\text{parameter_a} $$\n"
            report += "- **Steps:** Multiply historical_energy_consumption by parameter_a.\n"
            report += f"  - ${record['historical_energy_consumption']} \\times {record['parameter_a']} = {result['adjusted_consumption']}$\n"
            report += f"- **Final Adjusted Consumption:** **{result['adjusted_consumption']}**\n\n"
            
            report += "### 2. Time Adjustment Calculation\n"
            report += "- **Formula:** $$ \\text{Time Adjustment} = \\text{parameter_b} \\times \\text{forecast_time} $$\n"
            report += "- **Steps:** Multiply parameter_b by forecast_time.\n"
            report += f"  - ${record['parameter_b']} \\times {record['forecast_time']} = {result['time_adjustment']}$\n"
            report += f"- **Final Time Adjustment:** **{result['time_adjustment']}**\n\n"
            
            report += "### 3. Predicted Energy Consumption Calculation\n"
            report += "- **Formula:** $$ \\text{Predicted Energy} = \\text{baseline} + \\text{Adjusted Consumption} + \\text{Time Adjustment} $$\n"
            report += "- **Steps:** Sum baseline, Adjusted Consumption, and Time Adjustment.\n"
            report += f"  - ${record['baseline']} + {result['adjusted_consumption']} + {result['time_adjustment']} = {result['predicted_energy']}$\n"
            report += f"- **Final Predicted Energy:** **{result['predicted_energy']}**\n\n"
            
            report += "### 4. Relative Error Calculation\n"
            report += "- **Formula:** $$ \\text{Relative Error (\\%)} = \\left|\\frac{\\text{Predicted Energy} - \\text{historical_energy_consumption}}{\\text{historical_energy_consumption}}\\right| \\times 100 $$\n"
            report += "- **Steps:**\n"
            report += "  1. Subtract historical_energy_consumption from Predicted Energy.\n"
            report += f"     - ${result['predicted_energy']} - {record['historical_energy_consumption']} = {round(result['predicted_energy'] - record['historical_energy_consumption'], 2)}$\n"
            report += "  2. Divide the result by historical_energy_consumption.\n"
            report += f"     - ${round(result['predicted_energy'] - record['historical_energy_consumption'], 2)} \\div {record['historical_energy_consumption']} = {round((result['predicted_energy'] - record['historical_energy_consumption']) / record['historical_energy_consumption'], 4)}$\n"
            report += "  3. Multiply by 100.\n"
            report += f"     - ${round((result['predicted_energy'] - record['historical_energy_consumption']) / record['historical_energy_consumption'], 4)} \\times 100 = {round((result['predicted_energy'] - record['historical_energy_consumption']) / record['historical_energy_consumption'] * 100, 2)}$\n"
            report += "  4. Take the absolute value.\n"
            report += f"     - $|{round((result['predicted_energy'] - record['historical_energy_consumption']) / record['historical_energy_consumption'] * 100, 2)}| = {result['relative_error']}$\n"
            report += f"- **Final Relative Error:** **{result['relative_error']} %**\n\n"
            
            report += "### 5. Forecast Confidence Score Calculation\n"
            report += "- **Formula:** $$ \\text{Confidence Score} = 100 - \\text{Relative Error (\\%)} $$\n"
            report += "- **Steps:** Subtract the Relative Error from 100.\n"
            report += f"  - $100 - {result['relative_error']} = {result['confidence_score']}$\n"
            report += f"- **Final Confidence Score:** **{result['confidence_score']}**\n\n"
            
            report += "---\n\n"
            report += "## Final Recommendation\n\n"
            report += f"- **Relative Error:** **{result['relative_error']} %**\n"
            report += f"- **Confidence Score:** **{result['confidence_score']}**\n"
            report += f"- **Status:** {result['status']}\n"
            report += f"- **Recommended Action:** {result['recommendation']}\n\n"
        
        return report

    def process_data(self, data):
        """Process the data and generate reports"""
        print("Thank you for providing the data. I'll run some tests to check its validity.")
        
        if self.validate_data(data):
            validation_report = self.generate_validation_report()
            if self.records:
                results = self.calculate_predictions()
                forecast_report = self.generate_forecast_report(results)
                return validation_report + "\n\n" + forecast_report
            else:
                return validation_report
        else:
            return self.generate_validation_report()


# Example usage
def main():
    predictor = SmartGridEnergyPredictor()    
    data = """{
  "records": [
    {
      "timestamp": "2023-06-01T00:00:00Z",
      "historical_energy_consumption": 100,
      "parameter_a": 1.1,
      "parameter_b": 0.5,
      "forecast_time": 20,
      "baseline": 50
    },
    {
      "timestamp": "2023-06-02T00:00:00Z",
      "historical_energy_consumption": 120,
      "parameter_a": 1.2,
      "parameter_b": 0.55,
      "forecast_time": 15,
      "baseline": 55
    },
    {
      "timestamp": "2023-06-03T00:00:00Z",
      "historical_energy_consumption": 150,
      "parameter_a": 1.3,
      "parameter_b": 0.6,
      "forecast_time": 10,
      "baseline": 60
    },
    {
      "timestamp": "2023-06-04T00:00:00Z",
      "historical_energy_consumption": 130,
      "parameter_a": 1.15,
      "parameter_b": 0.65,
      "forecast_time": 25,
      "baseline": 65
    },
    {
      "timestamp": "2023-06-05T00:00:00Z",
      "historical_energy_consumption": 140,
      "parameter_a": 1.2,
      "parameter_b": 0.7,
      "forecast_time": 30,
      "baseline": 70
    },
    {
      "timestamp": "2023-06-06T00:00:00Z",
      "historical_energy_consumption": 160,
      "parameter_a": 1.25,
      "parameter_b": 0.75,
      "forecast_time": 12,
      "baseline": 75
    },
    {
      "timestamp": "2023-06-07T00:00:00Z",
      "historical_energy_consumption": 110,
      "parameter_a": 1.05,
      "parameter_b": 0.45,
      "forecast_time": 18,
      "baseline": 80
    },
    {
      "timestamp": "2023-06-08T00:00:00Z",
      "historical_energy_consumption": 170,
      "parameter_a": 1.3,
      "parameter_b": 0.55,
      "forecast_time": 22,
      "baseline": 85
    },
    {
      "timestamp": "2023-06-09T00:00:00Z",
      "historical_energy_consumption": 180,
      "parameter_a": 1.1,
      "parameter_b": 0.6,
      "forecast_time": 16,
      "baseline": 90
    },
    {
      "timestamp": "2023-06-10T00:00:00Z",
      "historical_energy_consumption": 190,
      "parameter_a": 1.2,
      "parameter_b": 0.5,
      "forecast_time": 14,
      "baseline": 95
    }
  ]
}

    """

    result = predictor.process_data(data)
    print(result)
# def main():
#     predictor = SmartGridEnergyPredictor()     
#     sample_csv = """timestamp,historical_energy_consumption,parameter_a,parameter_b,forecast_time,baseline
# 2023-02-10T00:00:00Z,110,1.1,0.45,20,55
# 2023-02-11T00:00:00Z,130,1.2,0.55,15,60
# 2023-02-12T00:00:00Z,175,1.3,0.65,30,50
# 2023-02-13T00:00:00Z,190,1.15,0.50,40,65
# 2023-02-14T00:00:00Z,160,1.25,0.70,25,70
# 2023-02-15T00:00:00Z,145,1.05,0.60,35,80
# 2023-02-16T00:00:00Z,155,1.3,0.55,10,75"""
#     result = predictor.process_data(sample_csv)
#     print(result)


if __name__ == "__main__":
    main()