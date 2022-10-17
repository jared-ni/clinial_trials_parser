import requests
import csv


class parser:
    # 3-tuple: (intervention, outcome, measurement)
    processed_data = []

    def __init__(self, data=[]):
        self.processed_Data = data

    def process_result(self, result, writer):

        outcomeMeasureTitle = result["OutcomeMeasureTitle"]
        outcomeGroup = result['OutcomeGroupList']['OutcomeGroup']
        outcomeData = (result['OutcomeClassList']['OutcomeClass'][0]['OutcomeCategoryList']
                            ['OutcomeCategory'][0]['OutcomeMeasurementList']['OutcomeMeasurement'])
        measurement_unit = result['OutcomeMeasureUnitOfMeasure']
        if "percentage of participants" in measurement_unit:
            measurement_unit = "%"

        # print(outcomeMeasureTitle)
        # print(outcomeGroup)
        # print(measurement_unit)
        # print(outcomeData)

        outcomesMap = { outcome['OutcomeGroupId']: {"intervention": outcome["OutcomeGroupTitle"]} for outcome in outcomeGroup }
        
        for measure in outcomeData:
            id = measure['OutcomeMeasurementGroupId']
            outcomesMap[id]["measurement"] = measure['OutcomeMeasurementValue'] + measurement_unit
            print(f'({outcomesMap[id]["intervention"]}, {outcomeMeasureTitle}, {outcomesMap[id]["measurement"]})')
            self.processed_data.append((outcomesMap[id]["intervention"], outcomeMeasureTitle, outcomesMap[id]["measurement"]))
            # writer.writerow(f'({outcomesMap[id]["intervention"]}, {outcomeMeasureTitle}, {outcomesMap[id]["measurement"]})')

    def start(self, NCTId):
        response = requests.get('http://ClinicalTrials.gov/api/query/full_studies', 
            params={"expr": NCTId,
                    "min_rank": 1, 
                    "max_rank": 1,
                    'fmt': "json"
                }
        )
        assert response.ok, "GET request failed"

        study = response.json()["FullStudiesResponse"]["FullStudies"][0]["Study"]
        results = study['ResultsSection']['OutcomeMeasuresModule']['OutcomeMeasureList']['OutcomeMeasure']

        with open('example.csv', 'w') as file:
            writer = csv.writer(file, delimiter=",")

            print("map")
            map(lambda r: (self.process_result(r, writer)), results)
            print(self.processed_Data)


if __name__ == '__main__':
    parser = parser()
    parser.start("NCT02684370")