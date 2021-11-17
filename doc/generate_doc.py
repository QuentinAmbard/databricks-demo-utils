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


def get_resources_html(resources):
    result = ""
    for resource_type in resources:
        html = ""
        for resource in resources[resource_type]:
            color = "primary"
            if resource_type == "DLT":
                color = "info"
            elif resource_type == "Queries":
                color = "success"

            html += f'<li><div class="dropdown-item">{resource} '
            for cloud in resources[resource_type][resource]:
                html += f' | <a target="_blank" href="{resources[resource_type][resource][cloud]}">{cloud}</a>'
            html += '</div></li>'
        result += f"""<div class="btn-group">
                        <button type="button" class="btn btn-{color} dropdown-toggle btn-sm" data-bs-toggle="dropdown" aria-expanded="false">{resource_type}</button>
                        <ul class="dropdown-menu">
                        {html}
                        </ul>
                    </div> """
    return result

def get_resources_html_for_node(node, resources):
    #match the resources by name, and then generate the html for the given resources.
    final_resources = {}
    if "db_resources" in node:
        for resource_type in node["db_resources"]:
            final_resources[resource_type] = {}
            for name in node["db_resources"][resource_type]:
                final_resources[resource_type][name] = resources[resource_type][name]
    return get_resources_html(final_resources)

def build_doc(node, html, id, i, resources):
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
                    {get_resources_html_for_node(node[k], resources)}
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
                <input type="checkbox" {'checked="checked"' if i < 1 else ''} id="c{id}_{i}" />
                <label class="tree_label" for="c{id}_{i}">{k}</label>"""
            html, i = build_doc(node[k], html, id, i + 1, resources)
            html +="""</li>"""
    html +="""</ul>"""
    return html, i

regex_retail = r'<\!\-\-\[__marker__\] \-\->(.|\n)*<\!\-\-\[__marker__\] \-\->'

def generate_vertical():
    with open("configuration.json", 'r') as file:
        data = json.loads(file.read())
        html = """<div class="container">"""
        i = j = k = l = 0
        for category in data:
            i+=1
            html += f"""<h2>{category}</h2><div class="row">"""
            for domain in data[category]:
                j+=1
                html += f"""<h4>{domain} <button type="button" class="btn btn-primary">Demo deck</button> <button type="button" class="btn btn-warning">Get .dbc archive</button></h4>
                            <div class="col-3">
                            <ul class="list-unstyled ps-0">"""
                for demo in data[category][domain]["demos"]:
                    k+=1
                    html += f"""
                        <li class="mb-1">
                            <button class="btn btn-toggle align-items-center rounded" data-bs-toggle="collapse" data-bs-target="#_{i}_{j}_{k}" aria-expanded="true">{demo["name"]}</button>
                            <div class="collapse show" id="_{i}_{j}_{k}" style="">
                                <ul class="btn-toggle-nav list-unstyled fw-normal pb-1 small">"""
                    for flow in demo["demo_flows"]:
                        l+=1
                        id = f"_{i}_{j}_{k}_{l}"
                        html += f"""<li style="clear: both"><button style="float: right" type="button" class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#{id}">Demo script</button>{flow}</li>"""
                        html += generate_script_modal(id, flow, demo["demo_flows"][flow]["script"], demo["demo_flows"][flow]["description"])
                    html += f"""</ul>
                            </div>
                        </li>"""
                html += "</ul>"
                resources = data[category][domain]["db_resources"]
                demo_folder = data[category][domain]["demo_folder"]
                node = documentation["."]["field-demo"][demo_folder]
                html_doc, _ = build_doc({demo_folder: node}, "", f"{i}_{j}", 0, resources)
                html_doc = """<h4>Ressources: """+get_resources_html(resources) +"""</h4>Notebooks:""" + html_doc
                html += f"""
                </div>
                <div class="col">
                <div class="tree">{html_doc}</div>
                </div></div><br/><br/>"""
        return """</div></div>"""+html


def generate_script_modal(id, name, script, description):
    html = f"""
    <div class="modal fade" id="{id}" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-xl">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="exampleModalLabel">{name}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
          <h3>Description</h3>{description} <br/><br/>
          <h3>High level Demo script</h3><br/>
            <div class="container">
              <div class="row row-cols-4">
                """
    i = 0
    for item in script:
        i += 1
        html += f"""<div class="col" style="min-height: 200px">
                    <div class="numberCircle">{i}</div>
                    <img width="200" src="https://databricks.com/wp-content/uploads/2021/10/db-nav-logo.svg"/>
                    <div>{item}</div>
                    </div>"""
    html += """
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            <button type="button" class="btn btn-primary">Save changes</button>
          </div>
        </div>
      </div>
    </div>"""
    return html


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