---
title: "Automating Data Governance: Building a Code and Lineage Scanner in Microsoft Fabric"
date: 2026-09-02
category: "Data Governance"
tags:
  - Microsoft Fabric
  - Data Engineering
  - Metadata
  - PySpark
  - Automated Governance
description: "How I built a custom PySpark scanner to automatically audit Microsoft Fabric notebooks and pipelines for coding standards, lineage, and governance compliance."
featured: false
---

## The Problem with Manual Governance

If you manage a growing data engineering environment, you eventually hit a scaling problem. You establish development standards—mandatory logging functions, parameter naming conventions, data retention checks, and strict architectural patterns—but enforcing them becomes a bottleneck.

In our Microsoft Fabric environment, we rely heavily on nested Data Pipelines orchestrating dozens (hundreds actually) of PySpark notebooks. We have rules: developers must use specific utility functions for path resolution (e.g., `getBronzeTablePath`), they must include data retention logging (`logDataRetention`), and they must not hardcode paths. These not only make code easier to review and understand but ensure we stick to legal retention policies. 

We also need to know exactly which notebooks write to which tables, and how parameters flow from a master pipeline down through various condition blocks into the final notebook execution. This helps ensure everything is configured correctly and allows for some basic data lineage without manuallly trawling through code, as we all know how much fun that can be!

Relying on manual code reviews to catch deviations in this kind of architecture is futile. People forget. Code gets copied and pasted. A parameter gets updated in a notebook but the overarching pipeline isn't updated to pass the new value, leading to silent failures or unexpected behaviour. I needed a way to audit our entire workspace programmatically. This can be a real problem when there are new or junior members in the team that are still grappling with new data and or technology and they are just trying to get things working. 

## The Approach: Treating Code as Data

Instead of relying on manual inspection, I decided to treat our Fabric workspace itself as a dataset. 

By leveraging PySpark, the `sempy` library, Fabric REST APIs, and `notebookutils`, I set out to build an automated scanner. The goal was to extract the JSON definition of every notebook and pipeline, parse the code, map the lineage, and surface compliance issues into a single, queryable DataFrame. Great for me to review and also useful for checking differnces between Dev and Prod when things aren't going as expected. 

The investigation naturally split into two halves: scanning the notebooks to understand what the code was doing, and scanning the pipelines to understand how that code was being orchestrated. 

## Implementation: Scanning the Codebase

The first step was establishing an accurate inventory of the workspace. Using `sempy.fabric`, I pulled the folder structures and mapped every notebook to its hierarchical path, allowing me to filter the scan to specific areas, like our BAU processes. We keep our code in a set folder structure and all code in our primary pipelines should be in the BAU folder, we didn't realise how useful that might be. 

Once I had the target list, I used `notebookutils.notebook.getDefinition()` to pull the raw `.ipynb` JSON for each notebook. From there, I used regular expressions to audit the Python code. Now lets be honest, nobody likes writing regex code from scratch and GenAI did a great job of putting the rules together for me. 

This allowed me to extract:
*   **Target Tables:** Identifying variables like `cTargetTableName`. Where is the data going. 
*   **Source Dependencies:** Capturing arguments passed to our internal path functions (`getBronzeTablePath`, `getSilverTablePath`, etc.). Where does the data come from. 
*   **Governance Compliance:** Checking for the presence of mandatory environment setups, verification checks, and specific logging functions like `writeLogEntry()` and data retention calls. 
*   **Code Smells:** Counting `.option("overwriteSchema", "true")` instances to spot potential data history wipes. Code smells was new to me but AI liked it. 

I initially ran into an issue where the scanner flagged missing `logDataRetention()` calls, even when developers had explicitly documented in a Markdown cell why it wasn't required for that specific table. I had to refine the logic to distinguish between code cells and markdown cells, ensuring the scanner could interpret a human-readable override (e.g., "no call to logDataRetention") and accurately report the status as "Not Required" rather than a compliance failure. FYI things like data retention are not needed when we are writing single one off monthly extracts, as people still love getting data in a csv. 

## Implementation: Decoding the Pipeline Lineage

Understanding the notebooks was only half the battle. A notebook's behavior is dictated by the parameters passed into it by the orchestrating pipeline. 

Extracting pipeline metadata proved far more complex than the notebooks. Fabric Data Pipelines are heavily nested JSON structures. A notebook execution might sit inside a `True` branch of an `IfCondition`, which itself sits inside a `ForEach` loop. Think notebooks that only run on certain conditions in a month, or reports that only get generated on 1st of a month.  

To map this, I wrote a recursive Python function that traversed the Fabric REST API (`/getDefinition`) payload for every pipeline in the workspace. It tracked the `_container_path` to build a true top-down lineage (e.g., `Root -> IfCondition(True) -> Load Silver Notebook`).

Here is a simplified version of the logic used to traverse the nested activities:

```python
def fGetDeepActivities(vActivities, vContainerPath="Root"):
    vResults = []
    if not vActivities: return vResults
    
    for vAct in vActivities:
        vAct["_container_path"] = vContainerPath
        vResults.append(vAct)
        
        vType = vAct.get("type")
        vProps = vAct.get("typeProperties", {})
        vActName = vAct.get("name", "Unknown")
        
        if vType == "IfCondition":
            vResults.extend(fGetDeepActivities(vProps.get("ifTrueActivities", []), f"{vContainerPath} -> {vActName}(True)"))
            vResults.extend(fGetDeepActivities(vProps.get("ifFalseActivities", []), f"{vContainerPath} -> {vActName}(False)"))
        elif vType in ["ForEach", "Until"]:
            vResults.extend(fGetDeepActivities(vProps.get("activities", []), f"{vContainerPath} -> {vActName}"))
        # ... handling for Switch statements and other containers
                
    return vResults
```

All of this came together to give me a dataframe with a raft of useful information, from the Notebook details, including last amended by due to our standard amendment log, through to the parent jobs in the pipeline that call it. 

## What Next

The above is great and we have found the output really useful, but I think we can take it further. We have plans to have this metadata stored in Dev, Test, Stage and Prod so that we can track changes over time. This will allow us to monitor changes to jobs, detect when deployments have gone wrong and if asked when code was changed we will have it all logged in a nice neat table. 

## My Learnings

This was one of my first projects lookg at what I could extract from Fabric and use the metadata. I certainly learnt a lot about how to do that and how flexible it can be as an environment. Plus, standards are hard to maintain but very important and we can use these processes to stop important things from going wrong. We have important data and need to make sure we don't keep data longer than we should, that controls are in place and that we have a concrete audit trail and this helps to enable us to do all of that. 