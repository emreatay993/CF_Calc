#calculate_and_plot_static_CF_for_linear_stress_in_ANSYS_v0.py

# Libraries
import csv
import context_menu
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import OpenFileDialog, DialogResult, MessageBoxButtons, MessageBoxIcon, MessageBox
import subprocess
import os

# Get all possible input data types from tree (it is EquivalentStress in this version of this code by default)
list_of_obj_of_all_result_objects = DataModel.Project.GetChildren(DataModelObjectCategory.Result,True)

list_of_obj_of_all_user_result_objects = DataModel.Project.GetChildren(DataModelObjectCategory.UserDefinedResult,True)

# Get the temperature distribution of the part vs NodeID for compensation factor calculation (from a user result)
list_of_obj_of_CF_Temp_input = [
    list_of_obj_of_all_user_result_objects[i]
    for i in range(len(list_of_obj_of_all_user_result_objects))
    if list_of_obj_of_all_user_result_objects[i].Name.Contains("CF_Temp")]

# Get input data at working temperature for compensation factor calculation
list_of_obj_of_CF_WT_input = [
    list_of_obj_of_all_result_objects[i]
    for i in range(len(list_of_obj_of_all_result_objects))
    if list_of_obj_of_all_result_objects[i].Name.Contains("CF_WT")]

# Get input data at room temperature for compensation factor calculation
list_of_obj_of_CF_RT_input = [
    list_of_obj_of_all_result_objects[i]
    for i in range(len(list_of_obj_of_all_result_objects))
    if list_of_obj_of_all_result_objects[i].Name.Contains("CF_RT")]

# Get the named selection of parts to be load compensated
obj_of_NS_parts_to_be_compensated = DataModel.GetObjectsByName("NS_parts_to_be_compensated")

# region Error Handling for Tree Objects - Named Selection
if len(obj_of_NS_parts_to_be_compensated) == 0:
    error_message = r"""A named selection called "NS_parts_to_be_compensated" is not created in the tree. This is required for visualizing the CF results on the screen. Please create the necessary named selection in the tree and try again. Also it is suggested to use this named selection as the scoping to prevent any error due to mismatch between the scopings of input contours to be used."""
    msg = Ansys.Mechanical.Application.Message(error_message, MessageSeverityType.Error)
    ExtAPI.Application.Messages.Add(msg)
    obj_of_NS_parts_to_be_compensated = Model.AddNamedSelection()
    exit()
    
if obj_of_NS_parts_to_be_compensated[0].ObjectState.ToString() != 'FullyDefined':
    error_message = r"""A named selection called "NS_parts_to_be_compensated" is created but it is suppressed in the tree. This is required for visualizing the CF results on the screen. Please fully define the necessary named selection in the tree and try again. Also it is suggested to use this named selection as the scoping to prevent any error due to mismatch between the scopings of input contours to be used."""
    msg = Ansys.Mechanical.Application.Message(error_message, MessageSeverityType.Error)
    ExtAPI.Application.Messages.Add(msg)
    obj_of_NS_parts_to_be_compensated = Model.AddNamedSelection()
    exit()
# endregion

# region Error Handling for Tree Objects, Input Data
if len(list_of_obj_of_CF_WT_input)==0 and len(list_of_obj_of_CF_RT_input)==0:
    error_message = r"""Contour results  which contain "CF_WT" and "CF_RT" prefix/suffix in their name are not defined. This is required for reading both "Node Number vs Value at Room Temperature" and "Node Number vs Value at Working Temperature" data. Please create both these objects in the tree and try again."""
    msg = Ansys.Mechanical.Application.Message(error_message, MessageSeverityType.Error)
    ExtAPI.Application.Messages.Add(msg)
    exit()
    
if len(list_of_obj_of_CF_WT_input)==0:
    error_message = r"""A contour result  which contains "CF_WT" prefix/suffix in its name is not defined.  This is required for reading the "Node Number vs Value at Working Temperature" data. Please create this object in the tree and try again."""
    msg = Ansys.Mechanical.Application.Message(error_message, MessageSeverityType.Error)
    ExtAPI.Application.Messages.Add(msg)
    exit()

if len(list_of_obj_of_CF_RT_input)==0:
    error_message = r"""A contour result  which contains "CF_RT" prefix/suffix in its name is not defined. This is required for reading the "Node Number vs Value at Room Temperature" data. Please create this object in the tree and try again."""
    msg = Ansys.Mechanical.Application.Message(error_message, MessageSeverityType.Error)
    ExtAPI.Application.Messages.Add(msg)
    exit()
    
if len(list_of_obj_of_CF_WT_input)>1:
    error_message = r"""There cannot be more than one contour with "CF_WT" prefix/suffix in its name in the tree."""
    msg = Ansys.Mechanical.Application.Message(error_message, MessageSeverityType.Error)
    ExtAPI.Application.Messages.Add(msg)
    exit()
    
if len(list_of_obj_of_CF_RT_input)>1:
    error_message = r"""There cannot be more than one contour with "CF_RT" prefix/suffix in its name in the tree."""
    msg = Ansys.Mechanical.Application.Message(error_message, MessageSeverityType.Error)
    ExtAPI.Application.Messages.Add(msg)
    exit()
    
if len(list_of_obj_of_CF_Temp_input)==0:
    error_message = r"""A  user defined result  which contains "CF_Temp" prefix/suffix in its name is not defined. The program will attempt to create and evaluate it automatically in the tree. This is required for reading the "Node Number vs Temperature" data. If it is not created automatically after this error message, please create this object manually in the tree and try again."""
    msg = Ansys.Mechanical.Application.Message(error_message, MessageSeverityType.Warning)
    ExtAPI.Application.Messages.Add(msg)
    solution_object_of_CF_WT_result = list_of_obj_of_CF_WT_input[0].Parent
    object_of_CF_Temp_result_created = solution_object_of_CF_WT_result.AddUserDefinedResult()
    object_of_CF_Temp_result_created.Name = "Compensated_Part_CF_Temp"
    object_of_CF_Temp_result_created.Expression = "BFE"
    object_of_CF_Temp_result_created.ScopingMethod=GeometryDefineByType.Component
    object_of_CF_Temp_result_created.AverageAcrossBodies = True
    object_of_CF_Temp_result_created.Location = obj_of_NS_parts_to_be_compensated[0]
    object_of_CF_Temp_result_created.Parent.EvaluateAllResults()

if len(list_of_obj_of_CF_Temp_input)>1:
    error_message = r"""There cannot be more than one user defined result with "CF_Temp" prefix/suffix in its name in the tree."""
    msg = Ansys.Mechanical.Application.Message(error_message, MessageSeverityType.Error)
    ExtAPI.Application.Messages.Add(msg)
    exit()
# endregion

if len(list_of_obj_of_CF_WT_input)==1 and len(list_of_obj_of_CF_RT_input)==1 and len(list_of_obj_of_CF_Temp_input):
    obj_of_CF_RT_input_data = list_of_obj_of_CF_RT_input[0]
    solver_files_directory_CF_RT_input = obj_of_CF_RT_input_data.Parent.WorkingDir
    file_path_CF_RT_input_txt = solver_files_directory_CF_RT_input + "CF_RT_input_data.txt"
    file_path_CF_RT_input_csv = solver_files_directory_CF_RT_input + "CF_RT_input_data.csv"
    obj_of_CF_RT_input_data.ExportToTextFile(file_path_CF_RT_input_txt)
    
    # Open the space-separated text file and the CSV file
    with open(file_path_CF_RT_input_txt, 'r') as text_file, open(file_path_CF_RT_input_csv, 'wb') as csv_file:
        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)
        
        # Read and write in chunks using list comprehension
        csv_writer.writerows([line.strip().split() for line in text_file])
        
    
    obj_of_CF_WT_input_data = list_of_obj_of_CF_WT_input[0]
    solver_files_directory_CF_WT_input = obj_of_CF_WT_input_data.Parent.WorkingDir
    file_path_CF_WT_input_txt = solver_files_directory_CF_WT_input + "CF_WT_input_data.txt"
    file_path_CF_WT_input_csv = solver_files_directory_CF_WT_input + "CF_WT_input_data.csv"
    obj_of_CF_WT_input_data.ExportToTextFile(file_path_CF_WT_input_txt)
    
    # Open the space-separated text file and the CSV file
    with open(file_path_CF_WT_input_txt, 'r') as text_file, open(file_path_CF_WT_input_csv, 'wb') as csv_file:
        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)
        
        # Read and write in chunks using list comprehension
        csv_writer.writerows([line.strip().split() for line in text_file])

    obj_of_CF_Temp_input_data = list_of_obj_of_CF_Temp_input[0]
    solver_files_directory_CF_Temp_input = obj_of_CF_Temp_input_data.Parent.WorkingDir
    file_path_CF_Temp_input_txt = solver_files_directory_CF_Temp_input + "CF_Temp_input_data.txt"
    file_path_CF_Temp_input_csv = solver_files_directory_CF_Temp_input + "CF_Temp_input_data.csv"
    obj_of_CF_Temp_input_data.ExportToTextFile(file_path_CF_Temp_input_txt)

    # Open the space-separated text file and the CSV file
    with open(file_path_CF_Temp_input_txt, 'r') as text_file, open(file_path_CF_Temp_input_csv, 'wb') as csv_file:
        # Create a CSV writer object
        csv_writer = csv.writer(csv_file)
        
        # Read and write in chunks using list comprehension
        csv_writer.writerows([line.strip().split() for line in text_file])

cpython_code = """
import numpy as np
from PyQt5.QtWidgets import QApplication, QFileDialog, QInputDialog
from scipy.interpolate import interp1d
import os

# Initialize a QApplication instance, which is required for PyQt5 dialogs
app = QApplication([])

# Dialog box class to select a file using PyQt5
class DialogBox:
    def __init__(self, title):
        self.filepath, _ = QFileDialog.getOpenFileName(caption=title, filter="CSV files (*.csv)")

    def get_file_path(self):
        return self.filepath

# User input form class to input room temperature using PyQt5
class UserInputForm:
    def __init__(self, prompt):
        self.input_value, ok = QInputDialog.getDouble(None, "Input", prompt, decimals=2)
        if not ok:  # If the user cancels the input dialog, exit the application
            sys.exit()

    def get_value(self):
        return self.input_value

# Function to read CSV and return columns as numpy arrays
def read_csv_columns(filepath):
    data = np.genfromtxt(filepath, delimiter=',', skip_header=1)
    return data[:, 0], data[:, 1]

# Using the PyQt5 dialog box instances to select CSV files
modulus_file_path = DialogBox("Select an input CSV file for Temperature [C] vs Young's Modulus [GPa] data").get_file_path()
yield_strength_file_path = DialogBox("Select an input CSV file for Temperature [C] vs Yield Strength [GPa] data").get_file_path()
node_temperature_file_path = r"{file_path_CF_Temp_input_csv}"
seqv_room_temp_file_path = r"{file_path_CF_RT_input_csv}"
seqv_working_temp_file_path = r"{file_path_CF_WT_input_csv}"

# Reading CSV files and assigning columns to variables
Temperature_of_Modulus, Modulus = read_csv_columns(modulus_file_path)
Temperature_of_Yield_Strength, Yield_Strength = read_csv_columns(yield_strength_file_path)
Node_Number, Temperature_of_Node = read_csv_columns(node_temperature_file_path)
Node_Number, SEQV_of_Node_at_Room_Temperature = read_csv_columns(seqv_room_temp_file_path)
Node_Number, SEQV_of_Node_at_Working_Temperature = read_csv_columns(seqv_working_temp_file_path)

# Function to interpolate modulus values at specific temperatures
def get_modulus_at_temp(temperature_of_node):
    interpolation = interp1d(Temperature_of_Modulus, Modulus, kind='linear', fill_value="extrapolate")
    return interpolation(temperature_of_node)

# Function to interpolate yield strength values at specific temperatures
def get_yield_strength_at_temp(temperature_of_node):
    interpolation = interp1d(Temperature_of_Yield_Strength, Yield_Strength, kind='linear', fill_value="extrapolate")
    return interpolation(temperature_of_node)

# Getting room temperature from user input
room_temperature_form = UserInputForm("Enter the room temperature of the test environment [C]:")
Room_Temperature = room_temperature_form.get_value()

# Calculating yield strength at room temperature
Yield_Strength_at_Room_Temperature = get_yield_strength_at_temp(np.array([Room_Temperature]))

# Function to calculate compensation factor
def calculate_compensation_factor(modulus_at_temp, yield_strength_at_work_temp, seqv_at_work_temp, seqv_at_room_temp):
    reserve_factor = yield_strength_at_work_temp / np.abs(seqv_at_work_temp)
    target_seqv_at_room_temp = Yield_Strength_at_Room_Temperature / reserve_factor
    static_compensation_factor = target_seqv_at_room_temp / seqv_at_room_temp
    return static_compensation_factor

# Assuming all Node_Number arrays are the same length for simplicity
Modulus_at_Temperature_of_Node = get_modulus_at_temp(Temperature_of_Node)
Yield_Strength_at_Working_Temperature_of_Node = get_yield_strength_at_temp(Temperature_of_Node)

# Calculate Static_Compensation_Factor_for_Target_SEQV
Static_Compensation_Factor_for_Target_SEQV = calculate_compensation_factor(Modulus_at_Temperature_of_Node, Yield_Strength_at_Working_Temperature_of_Node, SEQV_of_Node_at_Working_Temperature, SEQV_of_Node_at_Room_Temperature)

# Combine the two arrays column-wise
data_to_save = np.column_stack((Node_Number, Static_Compensation_Factor_for_Target_SEQV))

# Specify output csv directory
solver_files_directory_CF_WT_input = r"{solver_files_directory_CF_WT_input}"

# Specify the filename you want to save the data to
output_filepath_of_static_CF_csv = os.path.join(solver_files_directory_CF_WT_input, 'NodeID_vs_Static_CF_Result.csv')

# Save the combined data to a CSV file
np.savetxt(output_filepath_of_static_CF_csv, data_to_save, delimiter=',', header='Node_Number,Static_Compensation_Factor', comments='')
print(output_filepath_of_static_CF_csv)
""".format(solver_files_directory_CF_WT_input=solver_files_directory_CF_WT_input[:-1],
           file_path_CF_Temp_input_csv=file_path_CF_Temp_input_csv,
           file_path_CF_RT_input_csv=file_path_CF_RT_input_csv,
           file_path_CF_WT_input_csv=file_path_CF_WT_input_csv)

# Define the name of the cpython script to be run
cpython_script_name = "static_cf_calculation.py"
cpython_script_path = solver_files_directory_CF_WT_input + cpython_script_name

# Open a new Python file in write mode
with open(cpython_script_path, 'w') as file:
    # Write the content to the file
    file.write(cpython_code)

print("Python file created successfully.")

# Use subprocess to run the script
# If Python 3, you might need to use python3 in the command
subprocess.call(['python', cpython_script_path])

output_filepath_of_static_CF_csv = os.path.join(solver_files_directory_CF_WT_input, 'NodeID_vs_Static_CF_Result.csv')

# Visualize Static CF results using CSVPlot
contour_object_of_Static_CF_result = obj_of_CF_WT_input_data.Parent.Parent.CreateResultObject("csvPlot", "CSV Plot")
contour_object_of_Static_CF_result.Caption = "NodeID_vs_Static_CF_Result.csv"
contour_object_of_Static_CF_result.Properties[0].Properties[0].InternalValue = 'ID_NamedSelection'
contour_object_of_Static_CF_result.Properties[0].Properties[0].Properties[1].InternalValue = obj_of_NS_parts_to_be_compensated[0].ObjectId.ToString()
contour_object_of_Static_CF_result.Properties[1].InternalValue = output_filepath_of_static_CF_csv
contour_object_of_Static_CF_result.Properties[3].InternalValue = 'Static_Compensation_Factor'
contour_object_of_Static_CF_result.Properties[4].InternalValue = 'Node'
contour_object_of_Static_CF_result.Properties[5].InternalValue = 'No'
contour_object_of_Static_CF_result.Suppressed = 1
contour_object_of_Static_CF_result.Suppressed = 0

solution_object_of_contour_object_of_Static_CF_result = obj_of_CF_WT_input_data.Parent
solution_object_of_contour_object_of_Static_CF_result.EvaluateAllResults()
