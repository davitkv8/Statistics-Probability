import csv

input_file = 'population.csv'       # Replace with your actual filename
output_file = 'population.csv'      # We’ll overwrite the same file

# Step 1: Read all rows and apply 3% increase
with open(input_file, 'r') as f:
    reader = csv.reader(f)
    rows = [row for row in reader]

# Step 2: Convert values and apply the 15% increase
for i in range(len(rows)):
    try:
        original_value = float(rows[i][0])
        updated_value = round(original_value * 1.15, 2)  # Rounded to 2 decimals
        rows[i][0] = str(updated_value)
    except ValueError:
        # Skip header or invalid rows
        continue

# Step 3: Write updated values back to the file
with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)