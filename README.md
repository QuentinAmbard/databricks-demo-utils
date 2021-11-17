# Databricks utils

## Resource clone

### Setup:
Create a file named `config.json` and put your credential. You need to define the source (where the resources will be copied from) and a list of targets (where the resources will be cloned).

```json
{
  "source": {
    "url": "https://xxxxx.cloud.databricks.com",
    "token": "xxxxxxx",
    "job_prefixes": ["field_demo"], /* Job starting with these value will be deleted from target and cloned */ 
    "dlt_prefixes": ["field_demo"], /* DLT starting with these value will be deleted from target and cloned */
    "dashboard_tags": ["field_demos"] /* Dashboards having any of these tags matching will be deleted from target and cloned */
  },
  "targets": [
    {
      "url": "https:/xxxxxxx.cloud.databricks.com",
      "token": "xxxxxxx",
      "data_source_id": "xxxxxxxx-xxxx-xxxx-xxxx-a24894da3eaa"
    },
    {
      "url": "https://xxxxxxx.azuredatabricks.net",
      "token": "xxxxxxx",
      "data_source_id": "xxxxxxxx-xxxx-xxxx-xxxx-025befd8b98d"
    }
  ]
}
```
`data_source_id` is required and is the ID of the data source we'll attach to the queries/dashboard.
**This is NOT the endpoint ID that you can find in the URL**

To find your `data_source_id` on each target workspace:

- open your browser, edit an existing DBSQL query. 
- Assign the query to the SQL endpoint you want to be using
- Open the javascript console=>Network=>Filter on Fetch/XHR. 
- Click on the "Save" button of the DBSQL Query
- Open the corresponding Js query in the console 
  - click on the request "Preview"
  - search for `data_source_id`. That's the value you need to get

### Run:
Run the `clone_resources.py` script to clone all the ressources

## Custom clone
The clone utilities use a Client to identify source & target. Check `client.py` for more details.
### Custom Dashboard clone

Dashboard cloning is available in `copy_dashboard.py`.

By default, `copy_dashboard.delete_and_clone_dashboards_with_tags(source_client, dest_client, tags)` performs a DELETE on the tags matching in the target and re-create everything. It's not an UPDATE. 

It will first DELETE all the dashboard in the dest with the given tags, 
and then clone the dashboard from the source. 

If you need to copy without deleting, check `copy_dashboard.clone_dashboard_by_id(source_client: Client, dest_client: Client, dashboard_ids)`. Same logic could be applied to update instead.