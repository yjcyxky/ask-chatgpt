import pandas
import click
import json

if __name__ == "__main__":
    hp_table = pandas.read_csv("/Users/jy006/Documents/Code/biomedgps-data/databases/custom/formatted_hp.tsv", sep="\t")

    data = []

    question = "Please annotate the following table and output a table which contains three columns, one is the id, two is the name, and three is is_symptom. if an item is a symptom, please fill the is_symptom field a yes, otherwise no."

    def merge_rows(rows):
        output = "\n".join([f"{row['id']},{row['name']}" for i, row in rows.iterrows()])
        return "id,name\n" + output + "\n"

    # Loop the table by steps of 50
    step = 50
    for i in range(0, len(hp_table), step):
        # Get the next rows to process
        rows = hp_table[i : i + step]
        # Merge the rows into a string
        input = merge_rows(rows)
        # Add the question and input to the data
        data.append({"question": question, "input": input})

    with open("questions.json", "w") as f:
        json.dump(data, f)