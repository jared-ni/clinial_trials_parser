import requests
import csv


class parser:
    # 3-tuple: (intervention, outcome, measurement)
    processed_data = []


    def __init__(self, data=[]):
        self.processed_data = data


    def process_result(self, result):
        outcomeMeasureTitle = result["OutcomeMeasureTitle"]
        outcomeGroup = result['OutcomeGroupList']['OutcomeGroup']
        outcomeData = (result['OutcomeClassList']['OutcomeClass'][0]['OutcomeCategoryList']
                             ['OutcomeCategory'][0]['OutcomeMeasurementList']['OutcomeMeasurement'])
        measurement_unit = result['OutcomeMeasureUnitOfMeasure']
        measurement_unit = ("%" if "percentage of participants" in measurement_unit 
                                else " " + measurement_unit)

        outcomesMap = { outcome['OutcomeGroupId']: {"intervention": outcome["OutcomeGroupTitle"]} 
                    for outcome in outcomeGroup }
        
        for measure in outcomeData:
            id = measure['OutcomeMeasurementGroupId']
            outcomesMap[id]["measurement"] = measure['OutcomeMeasurementValue'] + measurement_unit
            self.processed_data.append((outcomesMap[id]["intervention"], 
                                        outcomeMeasureTitle, outcomesMap[id]["measurement"]))


    def start(self, NCTId):
        response = requests.get('http://ClinicalTrials.gov/api/query/full_studies', 
            params={   
                "expr": NCTId,
                "min_rank": 1, 
                "max_rank": 1,
                'fmt': "json"
        })
        assert response.ok, "GET request failed"

        study = response.json()["FullStudiesResponse"]["FullStudies"][0]["Study"]
        results = study['ResultsSection']['OutcomeMeasuresModule']['OutcomeMeasureList']['OutcomeMeasure']

        list(map(lambda r: self.process_result(r), results))
        return self.processed_data


if __name__ == '__main__':
    myParser = parser()
    processed_data = myParser.start("NCT02684370")

    with open("processed_data.csv", "wt") as fp:
        writer = csv.writer(fp, delimiter=",")
        
        for tuple in processed_data:
            writer.writerow(tuple)
        


    

    