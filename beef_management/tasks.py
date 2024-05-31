import frappe
import re

def updateSerialCostAfterMaterialIssue(doc):
    # Get Stock Entry Name From Request
    stock_entry_name = re.findall("\\((.*?)\\)", str(doc))
    # Get stock Entry Data 
    stock_entry = frappe.get_doc('Stock Entry', stock_entry_name[0])
    #Check if stock entry type is Material Issue or Material Transfer
    if (stock_entry.stock_entry_type == "Material Issue"):

        #Get the Details and set the number of actions required
        stock_entry_details = frappe.db.sql(f""" SELECT * FROM `tabStock Entry Detail` WHERE parent = "{stock_entry.name}" """, as_dict=True)

        #loop on Actions required
        for entry_detail in stock_entry_details:

            # Get if the Material Request is اعلاف
            if (entry_detail.item_group == "اعلاف" or entry_detail.item_group == "مركزات" or entry_detail.item_group == "بريمكسات"):
                # Get Material Request Item to set the Target Warehouse
                request_item = frappe.get_doc('Material Request Item', entry_detail.material_request_item)

                # Get Number of Items in the Target Warehouse
                target_warehouse_items = frappe.db.sql(f""" SELECT * FROM `tabSerial No` WHERE warehouse = "{request_item.warehouse}"; """, as_dict=True)

                # Get the Total Amount that need to be divided on the Target Warehouse Items
                total_action_cost = int(entry_detail.amount)

                # Check if Warehouse target is not empty (divided by zero error)
                if (len(target_warehouse_items) > 0):
                    # Get the amount that should be added to each Serial in the Target Warehouse
                    amout_per_serial = int(total_action_cost) / len(target_warehouse_items)
                    # Add cost for each Item
                    for item in target_warehouse_items: 
                        # Get the Serial No
                        doc = frappe.get_doc('Serial No', item['name'])
                        
                        # Check warehouse name and update accordingly
                        if (item['warehouse'] == "مخزن عجول الاستقبال - TKB"):
                            doc.cost_in_wh1 += amout_per_serial
                        elif (item['warehouse'] == "مخزن عجول تحت التشغيل - TKB"):
                            doc.cost_in_wh2 += amout_per_serial
                        elif (item['warehouse'] == "مخزن عجول نهائي - TKB"):
                            doc.cost_in_wh3 += amout_per_serial
                        
                        # Save Action
                        doc.save()

            # Check if the Item is أدوية and is added to Serial No Added in the Material Request
            elif (entry_detail.item_group == "أدوية"):

                # Get the Total Action cost According to Material Issue 
                total_action_cost = int(entry_detail.amount)

                # Get the Material Request associated to the Material Issue to select the Target Item
                material_request = frappe.get_doc('Material Request', entry_detail.material_request)

                # Select the Serial No
                target_item = frappe.get_doc('Serial No', material_request.serial_no)

                # Add the amount to the Requested Item in other Cost field
                target_item.other_costs += total_action_cost

                # Save Action
                target_item.save()
            
            else:
                pass

    elif (stock_entry.stock_entry_type == "Material Transfer"):
        stock_entry_details = frappe.db.sql(f""" SELECT * FROM `tabStock Entry Detail` WHERE parent = "{stock_entry.name}" """, as_dict=True)

        serials_list = list(stock_entry_details[0]['serial_no'].split('\n'))

        for serial in serials_list:
            
            if (stock_entry_details[0]['s_warehouse'] != stock_entry_details[0]['t_warehouse'] ):

                if (stock_entry_details[0]['s_warehouse'] == "مخزن عجول الاستقبال - TKB"):
                    serial_no = frappe.get_doc('Serial No', serial)
                    serial_no.wh1_exit_date = stock_entry.posting_date
                    serial_no.save()
                elif (stock_entry_details[0]['s_warehouse'] == "مخزن عجول تحت التشغيل - TKB"):
                    serial_no = frappe.get_doc('Serial No', serial)
                    serial_no.wh2_exit_date = stock_entry.posting_date
                    serial_no.save()
                elif (stock_entry_details[0]['s_warehouse'] == "مخزن عجول نهائي - TKB"):
                    serial_no = frappe.get_doc('Serial No', serial)
                    serial_no.wh3_exit_date = stock_entry.posting_date
                    serial_no.save()
                # else: 
                #     frappe.throw('This Transfer Can\'t be Done, Please Check with the Administrator')

    else:
        pass


def cancelSerialCostAfterMaterialIssue(doc):
    # Get Stock Entry Name From Request
    stock_entry_name = re.findall("\\((.*?)\\)", str(doc))
    # Get stock Entry Data 
    stock_entry = frappe.get_doc('Stock Entry', stock_entry_name[0])
    #Check if stock entry type is Material Issue or Material Transfer
    if (stock_entry.stock_entry_type == "Material Issue"):

        #Get the Details and set the number of actions required
        stock_entry_details = frappe.db.sql(f""" SELECT * FROM `tabStock Entry Detail` WHERE parent = "{stock_entry.name}" """, as_dict=True)

        #loop on Actions required
        for entry_detail in stock_entry_details:

            # Get if the Material Request is اعلاف
            if (entry_detail.item_group == "اعلاف" or entry_detail.item_group == "مركزات" or entry_detail.item_group == "بريمكسات"):
                # Get Material Request Item to set the Target Warehouse
                request_item = frappe.get_doc('Material Request Item', entry_detail.material_request_item)

                # Get Number of Items in the Target Warehouse
                target_warehouse_items = frappe.db.sql(f""" SELECT * FROM `tabSerial No` WHERE warehouse = "{request_item.warehouse}"; """, as_dict=True)

                # Get the Total Amount that need to be divided on the Target Warehouse Items
                total_action_cost = int(entry_detail.amount)

                # Check if Warehouse target is not empty (divided by zero error)
                if (len(target_warehouse_items) > 0):
                    # Get the amount that should be added to each Serial in the Target Warehouse
                    amout_per_serial = int(total_action_cost) / len(target_warehouse_items)
                    # Add cost for each Item
                    for item in target_warehouse_items: 
                        # Get the Serial No
                        doc = frappe.get_doc('Serial No', item['name'])
                        
                        # Check warehouse name and update accordingly
                        if (item['warehouse'] == "مخزن عجول الاستقبال - TKB" and doc.cost_in_wh1 >= 0):
                            if not doc.cost_in_wh1 < amout_per_serial:
                                doc.cost_in_wh1 -= amout_per_serial
                            else:
                                doc.cost_in_wh1 = 0.0
                        elif (item['warehouse'] == "مخزن عجول تحت التشغيل - TKB" and doc.cost_in_wh2 >= 0):
                            if not doc.cost_in_wh2 < amout_per_serial:
                                doc.cost_in_wh2 -= amout_per_serial
                            else:
                                doc.cost_in_wh2 = 0.0
                        elif (item['warehouse'] == "مخزن عجول نهائي - TKB" and doc.cost_in_wh3 >= 0):
                            if not doc.cost_in_wh3 < amout_per_serial:
                                doc.cost_in_wh3 -= amout_per_serial
                            else:
                                doc.cost_in_wh3 = 0.0
                        
                        # Save Action
                        doc.save()

            # Check if the Item is أدوية and is added to Serial No Added in the Material Request
            elif (entry_detail.item_group == "أدوية"):

                # Get the Total Action cost According to Material Issue 
                total_action_cost = int(entry_detail.amount)

                # Get the Material Request associated to the Material Issue to select the Target Item
                material_request = frappe.get_doc('Material Request', entry_detail.material_request)

                # Select the Serial No
                target_item = frappe.get_doc('Serial No', material_request.serial_no)

                # Add the amount to the Requested Item in other Cost field
                if not target_item.other_costs < total_action_cost:
                    target_item.other_costs -= total_action_cost
                else:
                    target_item.other_costs = 0.0

                # Save Action
                target_item.save()

            else:
                pass

    elif (stock_entry.stock_entry_type == "Material Transfer"):
        stock_entry_details = frappe.db.sql(f""" SELECT * FROM `tabStock Entry Detail` WHERE parent = "{stock_entry.name}" """, as_dict=True)

        serials_list = list(stock_entry_details[0]['serial_no'].split('\n'))

        for serial in serials_list:
            
            if (stock_entry_details[0]['s_warehouse'] != stock_entry_details[0]['t_warehouse'] ):

                if (stock_entry_details[0]['s_warehouse'] == "مخزن عجول الاستقبال - TKB"):
                    serial_no = frappe.get_doc('Serial No', serial)
                    serial_no.wh1_exit_date = None
                    serial_no.save()
                elif (stock_entry_details[0]['s_warehouse'] == "مخزن عجول تحت التشغيل - TKB"):
                    serial_no = frappe.get_doc('Serial No', serial)
                    serial_no.wh2_exit_date = None
                    serial_no.save()
                elif (stock_entry_details[0]['s_warehouse'] == "مخزن عجول نهائي - TKB"):
                    serial_no = frappe.get_doc('Serial No', serial)
                    serial_no.wh3_exit_date = None
                    serial_no.save()
                # else: 
                #     frappe.throw('This Transfer Can\'t be Done, Please Check with the Administrator')

def enqueueUpdateSerialCostAfterMaterialIssue(doc, event):
    frappe.enqueue(updateSerialCostAfterMaterialIssue, queue="default", is_async=True, doc=doc)

def enqueueCancelSerialCostAfterMaterialIssue(doc, event):
    frappe.enqueue(cancelSerialCostAfterMaterialIssue, queue="default", is_async=True, doc=doc)

