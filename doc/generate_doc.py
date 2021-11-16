import glob
import re
import os
import json
import traceback


regex_metadata = r'\[metadata=(\{.*\})\] *\-\->'
root = "./field-demo"
documentation = {}
for filename in glob.iglob(root+"/**", recursive=True):
    if os.path.isfile(filename) and not filename.startswith(root+"/bundle") and not filename.endswith("/"):
        with open(filename, 'r') as file:
            data = file.read()
            data = re.sub('\\n(#|--) *MAGIC', '', data)
            match = re.search(regex_metadata, data)
            metadata = {}
            if match:
                raw_data = match.group(1)
                try:
                    metadata = json.loads(raw_data)
                    doc_folder = metadata
                    print(metadata)
                    print(filename)
                except Exception as e:
                    traceback.format_exc()
                    print(f"error parsing json metadata. Please correct file {filename}")
                    print(f"Incorrect metadata: {raw_data}")
                    raise
            doc_folder = documentation
            for f in filename.split("/"):
                if filename.endswith(f):
                    doc_folder[f] = metadata
                elif f not in doc_folder:
                    doc_folder[f] = {}
                doc_folder = doc_folder[f]



def get_resources_html(node):
    result = ""
    if "db_resources" in node:
        for resource_type in node["db_resources"]:
            html = ""
            for resource in node["db_resources"][resource_type]:
                color = "primary"
                if resource_type == "DLT":
                    color = "info"
                elif resource_type == "Queries":
                    color = "success"

                html += f'<li><div class="dropdown-item">{resource} '
                for cloud in node["db_resources"][resource_type][resource]:
                    html += f' | <a target="_blank" href="{node["db_resources"][resource_type][resource][cloud]}">{cloud}</a>'
                html += '</div></li>'
            result += f"""<div class="btn-group">
                            <button type="button" class="btn btn-{color} dropdown-toggle btn-sm" data-bs-toggle="dropdown" aria-expanded="false">{resource_type}</button>
                            <ul class="dropdown-menu">
                            {html}
                            </ul>
                        </div> """
    return result


def get_all_resources_html(node):
    def get_all_resources(resources, node):
        for k in node.keys():
            if "db_resources" in node[k]:
                for r in node[k]["db_resources"]:
                    if r not in resources:
                        resources[r] = {}
                    #merge
                    for cloud in node[k]["db_resources"][r]:
                        if cloud not in resources[r]:
                            resources[r][cloud] = []
                        else:
                            resources[r][cloud] = node[k]["db_resources"][r][cloud]
            else:
                get_all_resources(resources, node[k])
    resources = {}
    get_all_resources(resources, node)
    return get_resources_html({"db_resources": resources})


def build_doc(node, html, i):
    html += """<ul>"""
    for k in sorted(node.keys()):
        if "description" in node[k]:
            if k.endswith(".py"):
                badge = "Python"
            elif k.endswith(".sql"):
                badge = "SQL"
            else:
                badge = "Scala"
            html +=f"""<li>
            <span class="tree_label">
                <div style="font-weight: bold;">
                    {k} <span class="badge rounded-pill bg-primary">{badge}</span>
                </div>
                <div style="float: right">
                    {get_resources_html(node[k])}
                </div>
 
                <div style="font-size: 14px;padding-left: 15px; width: 800px">
                    {node[k]["description"]}
                </div>
            </span></li>"""

        else:
            html +=f"""<li>"""
            if k.endswith(".py") or k.endswith(".sql") or k.endswith(".scala"):
                html +=f"""<span class="tree_label">{k}</span>"""
            else:
                html +=f"""
                <input type="checkbox" {'checked="checked"' if i<1 else ''} id="c{i}" />
                <label class="tree_label" for="c{i}">{k}</label>"""
            html, i = build_doc(node[k], html, i+1)
            html +="""</li>"""
    html +="""</ul>"""
    return html, i

regex_retail = r'<\!\-\-\[__marker__\] \-\->(.|\n)*<\!\-\-\[__marker__\] \-\->'

def generate_vertical():
    with open("configuration.json", 'r') as file:
        data = json.loads(file.read())
        html = """<div class="container">"""
        for category in data:
            html += f"""<h2>{category}</h2><div class="row">"""
            for domain in data[category]:
                html += f"""<h4>{domain} <button type="button" class="btn btn-primary">Demo deck</button> <button type="button" class="btn btn-warning">Get .dbc archive</button></h4>
                            <div class="col-3"><div class="list-group">"""
                for tech_persona in data[category][domain]["technical_personas"]["demo_flow"]:
                    html += f"""
                    
                    <a class="list-group-item list-group-item-action d-flex gap-3 py-3" aria-current="true">
                        <div class="d-flex gap-2 w-100 justify-content-between">
                                <div>
                                <h6 class="mb-0">{tech_persona}</h6>
                                <button type="button" class="btn btn-outline-warning btn-sm">How to run the demo</button>
                            </div>
                            <small class="opacity-50 text-nowrap">20min</small>
                        </div>
                    </a>"""
                html += "</div>"
                demo_folder = data[category][domain]["demo_folder"]
                node = documentation["."]["field-demo"][demo_folder]
                html_doc, _ = build_doc({demo_folder: node}, "", 0)
                html_doc = """<h4>Ressources: """+get_all_resources_html({demo_folder: node}) +"""</h4>""" + html_doc
                html += f"""
                </div>
                <div class="col">    
                <div class="tree">{html_doc}</div>
                </div></div><br/><br/>"""
        return """</div></div>"""+html




html_main = generate_vertical()

def replace_content(pattern, content):
    with open("template.html", 'r') as file:
        data = file.read()
        data = re.sub(regex_retail.replace("__marker__", pattern), f"<!--[{pattern}] --> \n" + content + f"\n<!--[{pattern}] -->", data)
    with open('template.html', 'w') as file:
        file.write(data)
print(regex_retail.replace("__marker__", "MAIN"))
replace_content("MAIN", html_main)

"""
with open("template.html", 'r') as file:
    data = file.read()
    data = re.sub(regex_retail, "<!--[RETAIL] --> \n" + html + "\n<!--[RETAIL] -->", data)
with open('template.html', 'w') as file:
    file.write(data)"""