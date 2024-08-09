import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.cost
#import ifcopenshell.util.cost.get_schedule_cost_items #pyright: ignore
import blenderbim.tool as tool #pyright: ignore
import pandas as pd
import os

import bpy #pyright: ignore
from bpy_extras.io_utils import ExportHelper #pyright: ignore
from bpy.types import Operator #pyright: ignore
from bpy.props import StringProperty #pyright: ignore


class TEST_OT_export_tst(Operator, ExportHelper):
    bl_idname = 'test.export_tst'
    bl_label = 'open'
    bl_options = {'PRESET', 'UNDO'}
    filename_ext = '.json'
    
    filter_glob: StringProperty( #pyright: ignore
        default='*.json',
        options={'HIDDEN'}
    )

    def execute(self, context): #pyright: ignore
        bpy.types.Scene.filepath = self.filepath
        return {'FINISHED'}

bpy.utils.register_class(TEST_OT_export_tst)

bpy.ops.test.export_tst('INVOKE_DEFAULT')

def get_cost_item(cost_schedule, cost_item_identification):
    """ Returns the cost item in the cost_schedule, searching for the cost_item_identification.
    If it is existing, it returns that, if it not existing in the cost_schedule it creates a new one"""
    cost_items = ifcopenshell.util.cost.get_schedule_cost_items(cost_schedule) #pyright: ignore
    is_existing = False
    cost_item = None
    for cost_it in cost_items:
        if cost_it.Identification == cost_item_identification:
            is_existing = True
            cost_item = cost_it
            break
        
    if not is_existing:
        cost_item = ifcopenshell.api.run("cost.add_cost_item", model, cost_schedule = cost_schedule)

    return cost_item

model = tool.Ifc.get()

cost_schedules = model.by_type("IfcCostSchedule")

boq_name = "CME"
sor_name = "EPU"
sor_divided_name = "EPU_ELEMENTARI"

def get_cost_schedule(name):
    is_existing = False
    cost_schedule = None
    for cost_sched in cost_schedules:
        if cost_sched.Name == name:
            is_existing = True
            cost_schedule = cost_sched
            break

    if not is_existing:
        if name == boq_name:
            predefined_type = "PRICEDBILLOFQUANTITIES"
        if name == sor_name:
            predefined_type = "SCHEDULEOFRATES"
        if name == sor_divided_name:
            predefined_type = "SCHEDULEOFRATES"
                
        cost_schedule = ifcopenshell.api.run(
            "cost.add_cost_schedule",
            model,
            name = name,
            predefined_type = predefined_type   #type: ignore
        )
    return cost_schedule

boq = get_cost_schedule(name = boq_name)
sor = get_cost_schedule(name = sor_name)
sor_divided = get_cost_schedule(name = sor_divided_name)

path = bpy.types.Scene.filepath
try:
    elenco_prezzi = pd.read_json(path, orient='records')
    if elenco_prezzi is None:
        raise ValueError("Il DataFrame ottenuto è None")
    if not isinstance(elenco_prezzi, pd.DataFrame):
        raise TypeError(f"L'oggetto ottenuto non è un DataFrame, ma è di tipo {type(elenco_prezzi)}")
except ValueError as ve:
    raise Exception(f"Errore di valore: {ve}")
except FileNotFoundError:
    raise Exception("File non trovato")
except TypeError as te:
    raise Exception(f"Errore di tipo: {te}")
except Exception as e:
    raise Exception(f"Errore durante la lettura del file JSON: {e}")

#codice = "VEN24-01.19.02.00"
codici = ["VEN24-01.19.02.00", #cartongesso
          "VEN24-01.05.14.b"] #demolizioni

for codice in codici:
    try:
        prezzo = elenco_prezzi[elenco_prezzi["Codice"] == codice]
        if prezzo is None or prezzo.empty:
            raise ValueError("Codice non trovato nel DataFrame")
    except KeyError as ke:
        raise Exception(f"Errore di chiave: {ke}")
    except ValueError as ve:
        raise Exception(f"Errore di valore: {ve}")
    except Exception as e:
        raise Exception(f"Errore durante la ricerca del codice: {e}")

    sor_cost_item = get_cost_item(sor, prezzo.Codice.iat[0])

    if sor_cost_item is not None:
        sor_cost_item.Identification = prezzo.Codice.iat[0]
        sor_cost_item.Name = prezzo.Descrizione.iat[0]
    else:
        raise ValueError("La voce di prezzo nell'EPU non può essere creata")

    value = ifcopenshell.api.run("cost.add_cost_value", model, parent=sor_cost_item)
    ifcopenshell.api.run(
        "cost.edit_cost_value",
        model,
        cost_value = value,
        attributes={"AppliedValue": prezzo.Prezzo.iat[0]},
    )

    #creo unità misura
    #    measure_class = ifcopenshell.util.unit.get_symbol_measure_class(prezzo.UMI.iat[0])
    #    value_component = model.create_entity(measure_class, 1)
    #    unit_component = model.create_unit(prezzo.UMI.iat[0])
    #    value.UnitBasis = model.createIfcMeasureWithUnit(value_component, unit_component)

    for sub_codice in prezzo.SUB.iat[0]:
        sub = elenco_prezzi[ elenco_prezzi["Codice"] == sub_codice]
        sub_cost_item = ifcopenshell.api.run("cost.add_cost_item", model, cost_item = sor_cost_item)
        if sub_cost_item is not None:
            sub_cost_item.Identification = sub.Codice.iat[0]
            sub_cost_item.Name = sub.Descrizione.iat[0]
        else:
            raise ValueError("La sub voce di prezzo nell'EPU non può essere creata")


        sub_cost_item_sor_divided = get_cost_item(
            cost_schedule = sor_divided,
            cost_item_identification= sub.Codice.iat[0]
        )
        if sub_cost_item_sor_divided is not None:
            sub_cost_item_sor_divided.Identification = sub.Codice.iat[0]
            sub_cost_item_sor_divided.Name = sub.Descrizione.iat[0]
        else:
            raise ValueError("La sub voce di prezzo nell'EPU Elementari non può essere creata")

        if not sub_cost_item_sor_divided.CostValues:
            value = ifcopenshell.api.run(
                "cost.add_cost_value",
                model,
                parent=sub_cost_item_sor_divided
            )
            ifcopenshell.api.run(
                "cost.edit_cost_value",
                model,
                cost_value = value,
                attributes={"AppliedValue": sub.Prezzo.iat[0]},
            )


        ifcopenshell.api.run(
            "cost.assign_cost_value",
            model,
            cost_item = sub_cost_item,
            cost_rate = sub_cost_item_sor_divided
        )
        #        value = ifcopenshell.api.run("cost.add_cost_value", model, parent = sub_cost_item)
        #        ifcopenshell.api.run(
        #            "cost.edit_cost_value",
        #            model,
        #            cost_value = value,
        #            attributes={"AppliedValue": sub.Prezzo.iat[0]},
        #        )

        




    boq_cost_item = ifcopenshell.api.run("cost.add_cost_item", model, cost_schedule=boq)
    boq_cost_item.Identification = prezzo.Codice.iat[0]
    boq_cost_item.Name = prezzo.Descrizione.iat[0]

    ifcopenshell.api.run("cost.assign_cost_value", model, cost_item = boq_cost_item , cost_rate = sor_cost_item)

    #print(f"CODICE {prezzo.Codice.iat[0]}")
    #print(f"DESCRIZIONE {prezzo.Descrizione.iat[0]}")
    #print(f"UMI {prezzo.UMI.iat[0]}")
    #print(f"PREZZO {prezzo.Prezzo.iat[0]}")
    #print(f"SGEUI {prezzo.SGEUI.iat[0]}")
    #print()
    #print(f"ELENCO SUB:")

    for sub_codice in prezzo.SUB.iat[0]:
        sub = elenco_prezzi[ elenco_prezzi["Codice"] == sub_codice]
        #print()
        #print(f"CODICE {sub.Codice.iat[0]}")
        #print(f"DESCRIZIONE {sub.Descrizione.iat[0]}")
        #print(f"UMI {sub.UMI.iat[0]}")
        #print(f"PREZZO {sub.Prezzo.iat[0]}")
        #if not np.isnan(sub.SGEUI.iat[0]):
        #    print(f"SGEUI {sub.SGEUI.iat[0]}")

