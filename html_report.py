import html
import json
import shutil
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
REFERENCE_WEB_STATIC = PROJECT_ROOT / "assets" / "web_static"
REFERENCE_TREE_MAPPING = REFERENCE_WEB_STATIC / "xmlfile" / "Fungtion_positive.json"
PROJECT_LOGO = PROJECT_ROOT / "assets" / "images" / "Fungtion_logo_with_white_text_dpi_72.png"
ASSET_PATHS = [
    "css/bootstrap-3.3.1.min.css",
    "css/bootstrap-theme-3.3.1.min.css",
    "css/bootstrap-table.min.css",
    "css/master-v=1438676717.css",
    "css/font-awesome.min.css",
    "css/googleapis.css",
    "fonts/FontAwesome.otf",
    "fonts/fontawesome-webfont.eot",
    "fonts/fontawesome-webfont.svg",
    "fonts/fontawesome-webfont.ttf",
    "fonts/fontawesome-webfont.woff",
    "fonts/glyphicons-halflings-regular-.eot",
    "fonts/glyphicons-halflings-regular.eot",
    "fonts/glyphicons-halflings-regular.svg",
    "fonts/glyphicons-halflings-regular.ttf",
    "fonts/glyphicons-halflings-regular.woff",
    "css/nouislider.min.css",
    "css/phylogram_d3_styles.css",
    "images/help.gif",
    "js/jquery-2.2.4.min.js",
    "js/bootstrap-3.3.6.min.js",
    "js/colorbrewer.min.js",
    "js/newick.js",
    "js/d3.v3.min.js",
    "js/nouislider.min.js",
    "js/echarts.min.js",
    "js/phylogram_d3/lib/tooltip.js",
    "js/phylogram_d3/phylogram_d3.js",
    "js/phylogram_d3/utils.js",
]


def _read_json_if_exists(path_value):
    if not path_value or pd.isna(path_value):
        return None
    path = Path(path_value)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def _read_text_if_exists(path_value):
    if not path_value or pd.isna(path_value):
        return ""
    path = Path(path_value)
    if not path.exists():
        return ""
    return path.read_text()


def _load_manifest(prediction_csv, manifest_csv=None):
    predictions = pd.read_csv(prediction_csv)
    if "type_link" not in predictions.columns:
        predictions["type_link"] = ""
    if manifest_csv and Path(manifest_csv).exists():
        manifest = pd.read_csv(manifest_csv)
        return predictions.merge(
            manifest[["header", "network_json", "tree_newick"]],
            on="header",
            how="left",
        )
    predictions["network_json"] = ""
    predictions["tree_newick"] = ""
    return predictions


def _copy_reference_assets(output_html, assets_dir=None):
    output_html = Path(output_html)
    if assets_dir:
        asset_root = Path(assets_dir)
    else:
        asset_root = output_html.with_name(output_html.stem + "_assets")
    for rel_path in ASSET_PATHS:
        src = REFERENCE_WEB_STATIC / rel_path
        dst = asset_root / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    if PROJECT_LOGO.exists():
        logo_dst = asset_root / "images" / PROJECT_LOGO.name
        logo_dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT_LOGO, logo_dst)
    return asset_root


def _reference_mapping_with_query(query_id):
    mapping = json.loads(REFERENCE_TREE_MAPPING.read_text())
    mapping.append(
        {
            "Protein ID": query_id,
            "Species": "Query protein",
            "SpeciesFirst": "Query",
            "Highlight": "yes",
        }
    )
    return mapping


def _write_network_page(output_path, rel_asset_prefix, seq_name, network_data):
    if network_data is None:
        body = """
        <div class="panel-body">
          <p style="padding: 24px;">No network visualization generated for this sequence.</p>
        </div>
        """
    else:
        body = f"""
        <div class="panel-body">
          <div id="container" style="background-color: #FFFFFF;height:1000px;width:100%"></div>
        </div>
        """

    output_path.write_text(
        f"""<!DOCTYPE html>
<html style="height: 100%">
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="{rel_asset_prefix}css/bootstrap-3.3.1.min.css">
  <link rel="stylesheet" type="text/css" href="{rel_asset_prefix}css/bootstrap-theme-3.3.1.min.css" media="screen,print" />
  <link rel="stylesheet" type="text/css" href="{rel_asset_prefix}css/bootstrap-table.min.css"/>
  <link rel="stylesheet" type="text/css" href="{rel_asset_prefix}css/master-v=1438676717.css" media="screen,print" />
  <link rel="stylesheet" type="text/css" href="{rel_asset_prefix}css/font-awesome.min.css"/>
  <link rel="stylesheet" type="text/css" href="{rel_asset_prefix}css/googleapis.css" />
  <style>
    body {{ margin: 0; background: #fff; }}
    .page-title {{ padding: 18px 20px 4px; font-size: 22px; }}
  </style>
</head>
<body>
  <div class="page-title">ESM-1b-based similarity network visualization for {html.escape(seq_name)}</div>
  {body}
  <script type="text/javascript" src="{rel_asset_prefix}js/jquery-2.2.4.min.js"></script>
  <script type="text/javascript" src="{rel_asset_prefix}js/bootstrap-3.3.6.min.js"></script>
  <script type="text/javascript" src="{rel_asset_prefix}js/echarts.min.js"></script>
  <script type="text/javascript">
    (function() {{
      var networkData = {json.dumps(network_data, ensure_ascii=False) if network_data is not None else 'null'};
      if (!networkData) {{
        return;
      }}
      var dom = document.getElementById("container");
      var myChart = echarts.init(dom, null, {{renderer: 'svg'}});
      var categories = [];
      var colors = [];
      networkData.nodes.map(function (node) {{
          if (categories.indexOf(node.species) < 0) {{
              categories[node.category] = {{name: node.species}};
          }}
          if (colors.indexOf(node.color) < 0) {{
              colors[node.category] = node.color;
          }}
      }});

      myChart.setOption({{
          title: {{ text: '' }},
          animationDurationUpdate: 1500,
          animationEasingUpdate: 'quinticInOut',
          color: colors,
          tooltip: {{
              formatter: function(params) {{
                  if (params.dataType === "node") {{
                      return '<div style="border-bottom: 1px solid rgb(255,255,255); font-size: 15px;padding-bottom: 7px;margin-bottom: 7px">' +
                          params.data["id"] + '</div>' + '- Species: ' + params.data["speciesfull"] + '</br>';
                  }}
                  if (params.dataType === "edge") {{
                      return params.data["source"] + "-->" + params.data["target"];
                  }}
              }}
          }},
          toolbox: {{
              show: false,
              feature: {{
                  restore: {{ show: true, title: "Refresh" }},
                  saveAsImage: {{ show: true, title: "Save As Image" }}
              }}
          }},
          legend: [{{
              data: categories.map(function (b) {{ return b && b.name; }}).filter(Boolean),
              orient: 'vertical',
              icon: 'circle',
              type: 'plain',
              left: 20,
              textStyle: {{ fontSize: 12 }}
          }}],
          series: [{{
              type: 'graph',
              layout: 'circular',
              draggable: false,
              animation: true,
              circular: {{ rotateLabel: true }},
              data: networkData.nodes.map(function (node) {{
                  var highlight = node.label;
                  if (highlight.indexOf("Query") > -1) {{
                      return {{
                          x: node.x,
                          y: node.y,
                          id: node.id,
                          name: node.label,
                          symbolSize: node.size * 1.5,
                          speciesfull: "-",
                          symbol: 'diamond',
                          label: {{ normal: {{ position: 'right', show: true, fontSize: 10 }} }},
                          itemStyle: {{
                              color: "#A01E31",
                              shadowBlur: 20,
                              borderWidth: 0,
                              borderColor: '#fff',
                              shadowColor: '#00ff00'
                          }}
                      }};
                  }}
                  return {{
                      x: node.x,
                      y: node.y,
                      id: node.id,
                      name: node.label,
                      symbolSize: node.freq * 2,
                      speciesfull: node.speciesfull,
                      label: {{ normal: {{ show: true, fontSize: 7 }} }},
                      itemStyle: {{
                          color: node.color,
                          shadowBlur: 10,
                          borderWidth: 1,
                          borderColor: '#fff',
                          shadowColor: 'rgba(0, 0, 0, 0.3)'
                      }},
                      category: node.category
                  }};
              }}),
              edges: networkData.edges.map(function (edge) {{
                  return {{ source: edge.sourceID, target: edge.targetID }};
              }}),
              emphasis: {{
                  label: {{ show: true, formatter: '{{b}}', position: 'right' }},
                  lineStyle: {{ width: 5 }}
              }},
              force: {{ repulsion: 300, edgeLength: 100 }},
              roam: true,
              focusNodeAdjacency: true,
              categories: categories,
              lineStyle: {{ color: 'source', width: 0.5, curveness: 0.3, opacity: 0.7 }}
          }}]
      }}, true);

      myChart.on('click', function (params) {{
          if (params.dataType !== 'node' || !params.data || !params.data.id) {{
              return;
          }}
          var label = String(params.data.id);
          if (label.indexOf('Query') > -1) {{
              return;
          }}
          var parts = label.split('|');
          if (parts.length < 2) {{
              return;
          }}
          var prefix = parts[0].toLowerCase();
          var accession = parts[1];
          if (!accession) {{
              return;
          }}
          if (prefix === 'tr' || prefix === 'sp') {{
              window.open('https://www.uniprot.org/uniprot/' + accession, '_blank');
              return;
          }}
          window.open('https://www.ncbi.nlm.nih.gov/protein/' + accession, '_blank');
      }});

      window.onresize = function() {{
          myChart.resize();
      }};
    }})();
  </script>
</body>
</html>"""
    )


def _write_tree_page(output_path, rel_asset_prefix, seq_name, newick_text, mapping_data):
    if not newick_text:
        body = """
        <div class="panel-body">
          <p style="padding: 24px;">No tree visualization generated for this sequence.</p>
        </div>
        """
    else:
        body = f"""
        <div id="container"></div>
        """

    output_path.write_text(
        f"""<!DOCTYPE html>
<html style="height: 100%">
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css">
  <link href="{rel_asset_prefix}css/bootstrap-3.3.1.min.css" rel="stylesheet">
  <link rel="stylesheet" type="text/css" href="{rel_asset_prefix}css/googleapis.css" />
  <link href="{rel_asset_prefix}css/nouislider.min.css" rel="stylesheet">
  <link href="{rel_asset_prefix}css/phylogram_d3_styles.css" rel="stylesheet">
  <style>
    body {{ height: 100%; margin: 0; background: #fff; }}
    #container {{ min-height: 1040px; }}
    .page-title {{ padding: 18px 20px 4px; font-size: 22px; }}
  </style>
</head>
<body>
  <div class="page-title">Relationship tree visualization for {html.escape(seq_name)}</div>
  {body}
  <script type="text/javascript" src="{rel_asset_prefix}js/jquery-2.2.4.min.js"></script>
  <script type="text/javascript" src="{rel_asset_prefix}js/bootstrap-3.3.6.min.js"></script>
  <script type="text/javascript" src="{rel_asset_prefix}js/colorbrewer.min.js"></script>
  <script type="text/javascript" src="{rel_asset_prefix}js/newick.js"></script>
  <script src="{rel_asset_prefix}js/d3.v3.min.js"></script>
  <script type="text/javascript" src="{rel_asset_prefix}js/phylogram_d3/lib/tooltip.js"></script>
  <script type="text/javascript" src="{rel_asset_prefix}js/nouislider.min.js"></script>
  <script type="text/javascript" src="{rel_asset_prefix}js/phylogram_d3/phylogram_d3.js"></script>
  <script type="text/javascript" src="{rel_asset_prefix}js/phylogram_d3/utils.js"></script>
  <script type="text/javascript">
    (function() {{
      var treeData = {json.dumps(newick_text) if newick_text else 'null'};
      if (!treeData) {{
        return;
      }}
      var treeOptions = {{
          mapping_dat: {json.dumps(mapping_data, ensure_ascii=False)},
          treeType: 'radial',
          hideRuler: false,
          skipBranchLengthScaling: false,
          skipLabels: false
      }};
      init(treeData, '#container', treeOptions, 1);
      window.onresize = function() {{
          fitTree(1);
      }};
    }})();
  </script>
</body>
</html>"""
    )


def generate_html_report(prediction_csv, output_html, manifest_csv=None, assets_dir=None):
    output_html = Path(output_html)
    output_html.parent.mkdir(parents=True, exist_ok=True)
    asset_root = _copy_reference_assets(output_html, assets_dir=assets_dir)
    entries_root = asset_root / "entries"
    entries_root.mkdir(parents=True, exist_ok=True)

    report_df = _load_manifest(prediction_csv, manifest_csv)
    total_sequences = len(report_df)
    positive_sequences = int((report_df["decision"].astype(str) == "yes").sum())
    logo_rel = f"{asset_root.name}/images/{PROJECT_LOGO.name}"
    rows = []

    for index, row in report_df.iterrows():
        slug = f"{index + 1:04d}"
        seq_dir = entries_root / slug
        seq_dir.mkdir(parents=True, exist_ok=True)
        rel_asset_prefix = "../../"

        network_data = _read_json_if_exists(row.get("network_json"))
        newick_text = _read_text_if_exists(row.get("tree_newick"))
        query_id = f"Query_{index + 1}"
        mapping_data = _reference_mapping_with_query(query_id)

        network_page = seq_dir / "network.html"
        tree_page = seq_dir / "tree.html"
        _write_network_page(network_page, rel_asset_prefix, str(row["header"]), network_data)
        _write_tree_page(tree_page, rel_asset_prefix, str(row["header"]), newick_text, mapping_data)

        decision = str(row["decision"])
        decision_label = "Yes" if decision == "yes" else "No"
        result_type = str(row.get("type", "Pred."))
        type_link = str(row.get("type_link", "") or "")
        if result_type == "Exp." and type_link:
            type_cell = f'<a href="{html.escape(type_link)}" target="_blank">Exp.</a>'
        else:
            type_cell = html.escape(result_type)
        if decision == "yes":
            network_button = (
                f'<a class="btn btn-primary btn-sm action-btn" href="{html.escape(str(network_page.relative_to(output_html.parent)))}" '
                f'target="_blank">Visualize</a>'
            )
            tree_button = (
                f'<a class="btn btn-primary btn-sm action-btn" href="{html.escape(str(tree_page.relative_to(output_html.parent)))}" '
                f'target="_blank">Visualize</a>'
            )
        else:
            network_button = '<span class="text-muted">-</span>'
            tree_button = '<span class="text-muted">-</span>'

        rows.append(
            f"""
            <tr data-sort-no="{index + 1}" data-sort-name="{html.escape(str(row['header']).lower())}" data-sort-score="{float(row['score']) if str(row['score']) != '1' else 1.0}" data-sort-effector="{decision_label.lower()}" data-sort-type="{html.escape(result_type.lower())}">
              <td>{index + 1}</td>
              <td>{html.escape(str(row["header"]))}</td>
              <td class="center-cell">{html.escape(str(row["score"]))}</td>
              <td class="center-cell">{decision_label}</td>
              <td class="center-cell">{type_cell}</td>
              <td class="center-cell action-cell">{network_button}</td>
              <td class="center-cell action-cell">{tree_button}</td>
            </tr>
            """
        )

    output_html.write_text(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Prediction Results</title>
  <link href="{asset_root.name}/css/bootstrap-3.3.1.min.css" rel="stylesheet">
  <link rel="stylesheet" type="text/css" href="{asset_root.name}/css/bootstrap-theme-3.3.1.min.css" media="screen,print" />
  <link rel="stylesheet" type="text/css" href="{asset_root.name}/css/bootstrap-table.min.css"/>
  <link rel="stylesheet" type="text/css" href="{asset_root.name}/css/master-v=1438676717.css" media="screen,print" />
  <link rel="stylesheet" type="text/css" href="{asset_root.name}/css/font-awesome.min.css"/>
  <style>
    body {{
      background: #fff;
      padding-top: 74px;
    }}
    .navbar {{
      min-height: 56px;
      padding-left: 20px;
      padding-right: 25px;
    }}
    .navbar-brand {{
      height: 56px;
      padding: 10px 15px;
    }}
    .navbar-brand img {{
      height: 30px;
      width: auto;
    }}
    #main-content {{
      padding-left: 32px;
      padding-right: 32px;
      padding-bottom: 28px;
    }}
    .section-title {{
      padding-bottom: 12px;
      margin-top: 2px;
    }}
    .section-title i {{
      vertical-align: middle;
    }}
    .section-title .title-text {{
      margin-top: 0;
      margin-bottom: 0;
      font-size: 28px;
      font-weight: 700;
      vertical-align: middle;
      margin-left: 8px;
      display: inline-block;
    }}
    .summary-well {{
      padding: 15px;
      margin-bottom: 22px;
    }}
    .citation-well {{
      margin-top: 24px;
      margin-bottom: 8px;
    }}
    .summary-box {{
      border: 1px solid transparent;
      border-radius: 4px;
      font-size: 15px;
      line-height: 1.75;
    }}
    .summary-label {{
      font-weight: 700;
    }}
    .result-wrap {{
      background: #fff;
      border: 1px solid #ddd;
      border-radius: 4px;
      padding: 0;
      overflow: hidden;
    }}
    .table-toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      border-bottom: 1px solid #e5e5e5;
      background: #fff;
    }}
    .toolbar-left,
    .toolbar-right {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .toolbar-search {{
      width: 220px;
    }}
    .toolbar-btn {{
      min-width: 38px;
      padding-left: 10px;
      padding-right: 10px;
    }}
    .columns-menu {{
      min-width: 230px;
      padding: 8px 0;
    }}
    .columns-menu label {{
      display: block;
      font-weight: 400;
      padding: 4px 16px;
      margin: 0;
      cursor: pointer;
    }}
    .columns-menu input {{
      margin-right: 8px;
    }}
    .result-head {{
      padding: 16px 20px;
      border-bottom: 1px solid #e5e5e5;
      background: #fcfcfc;
    }}
    .result-head h3 {{
      margin: 0;
      font-size: 22px;
    }}
    .table {{
      margin-bottom: 0;
    }}
    .table > thead > tr > th,
    .table > tbody > tr > td {{
      vertical-align: middle !important;
    }}
    .center-cell {{
      text-align: center;
    }}
    .action-btn {{
      min-width: 82px;
    }}
    .table > thead > tr:first-child > th {{
      padding-left: 8px;
      padding-top: 4px;
      padding-bottom: 4px;
    }}
    .table > thead > tr:nth-child(2) > th {{
      padding-left: 8px;
      padding-top: 4px;
      padding-bottom: 4px;
    }}
    .sortable-header {{
      cursor: pointer;
      user-select: none;
    }}
    .sortable-header .sort-label {{
      display: inline-block;
      padding-right: 16px;
      position: relative;
    }}
    .sortable-header .sort-label:after {{
      content: '\\2195';
      position: absolute;
      right: 0;
      top: 0;
      color: #bcbcbc;
      font-size: 12px;
      line-height: 1.2;
    }}
    .sortable-header.sort-asc .sort-label:after {{
      content: '\\2191';
      color: #337ab7;
    }}
    .sortable-header.sort-desc .sort-label:after {{
      content: '\\2193';
      color: #337ab7;
    }}
    .pagination-wrap {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 14px 20px 16px;
      border-top: 1px solid #e5e5e5;
      background: #fcfcfc;
    }}
    .showing-rows {{
      color: #333;
      font-size: 13px;
    }}
    .pagination {{
      margin: 0;
    }}
    .pagination > li > a,
    .pagination > li > span {{
      color: #337ab7;
    }}
    .pagination > .active > a,
    .pagination > .active > span,
    .pagination > .active > a:hover,
    .pagination > .active > span:hover,
    .pagination > .active > a:focus,
    .pagination > .active > span:focus {{
      background-color: #337ab7;
      border-color: #337ab7;
    }}
    @media (max-width: 991px) {{
      body {{
        padding-top: 66px;
      }}
      #main-content {{
        padding-left: 12px;
        padding-right: 12px;
      }}
      .section-title .title-text {{
        font-size: 24px;
      }}
      .table-toolbar {{
        flex-direction: column;
        align-items: stretch;
      }}
      .toolbar-left,
      .toolbar-right {{
        justify-content: flex-start;
      }}
      .toolbar-search {{
        width: 100%;
      }}
    }}
  </style>
</head>
<body>
  <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
    <div class="container-fluid">
      <div class="navbar-header" style="width: 40%">
        <button aria-controls="navbar" aria-expanded="false"
          data-target=".collapseThis" data-toggle="collapse"
          class="navbar-toggle collapsed" type="button">
          <span class="sr-only">Toggle navigation</span><span class="icon-bar"></span><span
            class="icon-bar"></span><span class="icon-bar"></span>
        </button>
        <a class="navbar-brand" href="#">
          <img src="{logo_rel}" alt="Fungtion logo" />
        </a>
      </div>
    </div>
  </nav>

  <div id="tools"></div>
  <div id="main-content">
    <div class="section-title">
      <i class="icon-cloud icon-2x"></i><span class="title-text">Prediction Results</span>
    </div>

    <div class="well well-lg summary-well">
      <div class="summary-box row">
        <div class="col-sm-6">
          <div><span class="summary-label">Mode:</span> <em>Default mode</em></div>
          <div><span class="summary-label">Sequence Number:</span> <em>{total_sequences}</em></div>
        </div>
        <div class="col-sm-6">
          <div><span class="summary-label">Usage:</span> <em>Local report</em></div>
          <div><span class="summary-label">Predicted as fungal effectors:</span> <em>{positive_sequences}</em></div>
        </div>
      </div>
    </div>

    <div class="result-wrap">
      <div class="table-toolbar">
        <div class="toolbar-left">
          <div class="btn-group">
            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
              Export Basic <span class="caret"></span>
            </button>
            <ul class="dropdown-menu" role="menu">
              <li><a href="#" id="export-current">Export Current View (CSV)</a></li>
              <li><a href="#" id="export-all">Export All Rows (CSV)</a></li>
            </ul>
          </div>
        </div>
        <div class="toolbar-right">
          <input type="text" class="form-control toolbar-search" id="table-search" placeholder="Search">
          <button type="button" class="btn btn-default toolbar-btn" id="refresh-table" title="Refresh"><i class="icon-refresh"></i></button>
          <div class="btn-group">
            <button type="button" class="btn btn-default toolbar-btn dropdown-toggle" data-toggle="dropdown" title="Columns" aria-expanded="false">
              <i class="icon-th"></i>
            </button>
            <ul class="dropdown-menu dropdown-menu-right columns-menu" role="menu" id="columns-menu">
              <li><label><input type="checkbox" data-column-index="0" checked> No.</label></li>
              <li><label><input type="checkbox" data-column-index="1" checked> Name</label></li>
              <li><label><input type="checkbox" data-column-index="2" checked> Score</label></li>
              <li><label><input type="checkbox" data-column-index="3" checked> Fungal effector</label></li>
              <li><label><input type="checkbox" data-column-index="4" checked> Type</label></li>
              <li><label><input type="checkbox" data-column-index="5" checked> ESM-1b-based similarity network</label></li>
              <li><label><input type="checkbox" data-column-index="6" checked> Relationship tree</label></li>
            </ul>
          </div>
        </div>
      </div>
      <div class="table-responsive">
        <table class="table table-striped table-hover" id="results-table">
          <thead>
            <tr>
              <th data-colspan="2">Protein Info</th>
              <th data-colspan="5">Prediction Results</th>
            </tr>
            <tr>
              <th class="sortable-header" data-sort-key="no" data-sort-type="number"><span class="sort-label">No.</span></th>
              <th class="sortable-header" data-sort-key="name" data-sort-type="text"><span class="sort-label">Name</span></th>
              <th class="center-cell sortable-header" data-sort-key="score" data-sort-type="number"><span class="sort-label">Score</span> <img id="score-help" src="{asset_root.name}/images/help.gif" width="12" height="12" title="Score" data-content="The annotation of the Score:<ul><li>The number in each column denotes the probability of a query sequence is likely to be a fungal effector.</li><li>By directly clicking the header of this column, users will get a ranked list of the predicted results.</li></ul>" data-placement="top" /></th>
              <th class="center-cell sortable-header" data-sort-key="effector" data-sort-type="text"><span class="sort-label">Fungal effector</span> <img id="effector-help" src="{asset_root.name}/images/help.gif" width="12" height="12" title="Fungal effector" data-content="The annotation of results:<ul><li>'Yes' denotes that the sequence is a fungal effector.</li><li>'No' denotes that the sequence is not a fungal effector.</li></ul>" data-placement="top" /></th>
              <th class="center-cell sortable-header" data-sort-key="type" data-sort-type="text"><span class="sort-label">Type</span> <img id="type-help" src="{asset_root.name}/images/help.gif" width="12" height="12" title="Type" data-content="The annotation of the type results:<ul><li>'Exp.' denotes that the result was validated by wet lab experiments.</li><li>'Pred.' denotes that the result was predicted using Fungtion.</li></ul>" data-placement="top" /></th>
              <th class="center-cell">ESM-1b-based similarity network <img id="network-help" src="{asset_root.name}/images/help.gif" width="12" height="12" title="ESM-1b-based similarity network" data-content="If an inquiry protein was predicted as a fungal effector, its ESM-1b-based similarity network with known fungal effectors will be visualized, to facilitate user infer its potential subtype, biochemical properties and functions." data-placement="top" /></th>
              <th class="center-cell">Relationship tree <img id="tree-help" src="{asset_root.name}/images/help.gif" width="12" height="12" title="Relationship tree" data-content="If an inquiry protein was predicted as a fungal effector, its evolutionary relationships with known fungal effectors will be visualized, to facilitate user infer its potential subtype, biochemical properties and functions." data-placement="top" /></th>
            </tr>
          </thead>
          <tbody id="results-body">
            {''.join(rows)}
          </tbody>
        </table>
      </div>
      <div class="pagination-wrap">
        <div class="showing-rows" id="showing-rows"></div>
        <ul class="pagination" id="pagination"></ul>
      </div>
    </div>

    <div class="well well-lg citation-well">
      <b><font size=+2>I</font></b>f you find our work useful for your research work, please cite:
      <ul>
        <li>Li J, Ren J, Dai W <em>et al.</em> Fungtion: a server for predicting and visualizing fungal effector proteins. 2024, <em>Journal of Molecular Biology.</em> <a href="https://doi.org/10.1016/j.jmb.2024.168613" target="_blank" rel="noopener noreferrer">DOI: 10.1016/j.jmb.2024.168613</a></li>
      </ul>
    </div>
  </div>
  <script type="text/javascript" src="{asset_root.name}/js/jquery-2.2.4.min.js"></script>
  <script type="text/javascript" src="{asset_root.name}/js/bootstrap-3.3.6.min.js"></script>
  <script type="text/javascript">
    (function() {{
      if (window.jQuery && jQuery.fn.popover) {{
        jQuery('#score-help').popover({{
          trigger: 'hover',
          html: true
        }});
        jQuery('#effector-help').popover({{
          trigger: 'hover',
          html: true
        }});
        jQuery('#type-help').popover({{
          trigger: 'hover',
          html: true
        }});
        jQuery('#network-help').popover({{
          trigger: 'hover',
          html: true
        }});
        jQuery('#tree-help').popover({{
          trigger: 'hover',
          html: true
        }});
      }}

      var rowsPerPage = 15;
      var tbody = document.getElementById('results-body');
      var rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
      var allRows = rows.slice();
      var pagination = document.getElementById('pagination');
      var showingRows = document.getElementById('showing-rows');
      var sortableHeaders = Array.prototype.slice.call(document.querySelectorAll('.sortable-header'));
      var searchInput = document.getElementById('table-search');
      var refreshButton = document.getElementById('refresh-table');
      var columnToggles = Array.prototype.slice.call(document.querySelectorAll('#columns-menu input[type="checkbox"]'));
      var totalPages = Math.max(1, Math.ceil(rows.length / rowsPerPage));
      var currentPage = 1;
      var currentSortKey = null;
      var currentSortDirection = 'asc';
      var currentSearch = '';

      function updateTotals() {{
        totalPages = Math.max(1, Math.ceil(rows.length / rowsPerPage));
        if (currentPage > totalPages) {{
          currentPage = totalPages;
        }}
      }}

      function updateSortIndicators() {{
        sortableHeaders.forEach(function(header) {{
          header.classList.remove('sort-asc');
          header.classList.remove('sort-desc');
          if (header.getAttribute('data-sort-key') === currentSortKey) {{
            header.classList.add(currentSortDirection === 'asc' ? 'sort-asc' : 'sort-desc');
          }}
        }});
      }}

      function sortRows(sortKey, sortType) {{
        allRows.sort(function(a, b) {{
          var aValue = a.getAttribute('data-sort-' + sortKey) || '';
          var bValue = b.getAttribute('data-sort-' + sortKey) || '';
          if (sortType === 'number') {{
            aValue = parseFloat(aValue);
            bValue = parseFloat(bValue);
          }} else {{
            aValue = aValue.toLowerCase();
            bValue = bValue.toLowerCase();
          }}
          if (aValue < bValue) {{
            return currentSortDirection === 'asc' ? -1 : 1;
          }}
          if (aValue > bValue) {{
            return currentSortDirection === 'asc' ? 1 : -1;
          }}
          var aNo = parseFloat(a.getAttribute('data-sort-no') || '0');
          var bNo = parseFloat(b.getAttribute('data-sort-no') || '0');
          return aNo - bNo;
        }});
        updateSortIndicators();
        applyFiltersAndRender(1);
      }}

      function applyColumnVisibility() {{
        columnToggles.forEach(function(toggle) {{
          var columnIndex = parseInt(toggle.getAttribute('data-column-index'), 10);
          var displayValue = toggle.checked ? '' : 'none';
          document.querySelectorAll('#results-table tr').forEach(function(row) {{
            if (row.children[columnIndex]) {{
              row.children[columnIndex].style.display = displayValue;
            }}
          }});
        }});
      }}

      function filterRows() {{
        var term = currentSearch.trim().toLowerCase();
        rows = allRows.filter(function(row) {{
          if (!term) {{
            return true;
          }}
          return row.textContent.toLowerCase().indexOf(term) > -1;
        }});
        rows.forEach(function(row) {{
          tbody.appendChild(row);
        }});
        updateTotals();
      }}

      function renderPagination() {{
        pagination.innerHTML = '';

        function addItem(label, page, disabled, active) {{
          var li = document.createElement('li');
          if (disabled) li.className = 'disabled';
          if (active) li.className = 'active';
          var a = document.createElement('a');
          a.href = '#';
          a.textContent = label;
          a.addEventListener('click', function(event) {{
            event.preventDefault();
            if (disabled || active) return;
            renderPage(page);
          }});
          li.appendChild(a);
          pagination.appendChild(li);
        }}

        addItem('«', Math.max(1, currentPage - 1), currentPage === 1, false);
        for (var page = 1; page <= totalPages; page += 1) {{
          addItem(String(page), page, false, page === currentPage);
        }}
        addItem('»', Math.min(totalPages, currentPage + 1), currentPage === totalPages, false);
      }}

      function renderPage(page) {{
        currentPage = page;
        var start = (page - 1) * rowsPerPage;
        var end = start + rowsPerPage;
        allRows.forEach(function(row) {{
          row.style.display = 'none';
        }});
        rows.forEach(function(row, index) {{
          row.style.display = (index >= start && index < end) ? '' : 'none';
        }});
        var shownFrom = rows.length === 0 ? 0 : start + 1;
        var shownTo = Math.min(end, rows.length);
        showingRows.textContent = 'Showing ' + shownFrom + ' to ' + shownTo + ' of ' + rows.length + ' rows';
        applyColumnVisibility();
        renderPagination();
      }}

      function applyFiltersAndRender(page) {{
        filterRows();
        renderPage(page || 1);
      }}

      function exportRows(exportAll) {{
        var sourceRows = exportAll ? rows : rows.filter(function(_row, index) {{
          var start = (currentPage - 1) * rowsPerPage;
          var end = start + rowsPerPage;
          return index >= start && index < end;
        }});
        var visibleColumns = columnToggles
          .filter(function(toggle) {{ return toggle.checked; }})
          .map(function(toggle) {{ return parseInt(toggle.getAttribute('data-column-index'), 10); }});
        var headerCells = Array.prototype.slice.call(document.querySelectorAll('#results-table thead tr:nth-child(2) th'));
        var csvLines = [];
        csvLines.push(visibleColumns.map(function(index) {{
          return '"' + headerCells[index].innerText.replace(/"/g, '""').trim() + '"';
        }}).join(','));
        sourceRows.forEach(function(row) {{
          var cells = Array.prototype.slice.call(row.children);
          csvLines.push(visibleColumns.map(function(index) {{
            return '"' + (cells[index] ? cells[index].innerText : '').replace(/"/g, '""').trim() + '"';
          }}).join(','));
        }});
        var blob = new Blob([csvLines.join('\\n')], {{ type: 'text/csv;charset=utf-8;' }});
        var url = URL.createObjectURL(blob);
        var link = document.createElement('a');
        link.href = url;
        link.download = exportAll ? 'prediction_results_all.csv' : 'prediction_results_current_view.csv';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }}

      sortableHeaders.forEach(function(header) {{
        header.addEventListener('click', function(event) {{
          if (event.target && event.target.tagName === 'IMG') {{
            return;
          }}
          var sortKey = header.getAttribute('data-sort-key');
          var sortType = header.getAttribute('data-sort-type') || 'text';
          if (currentSortKey === sortKey) {{
            currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
          }} else {{
            currentSortKey = sortKey;
            currentSortDirection = 'asc';
          }}
          sortRows(sortKey, sortType);
        }});
      }});

      if (searchInput) {{
        searchInput.addEventListener('input', function() {{
          currentSearch = searchInput.value || '';
          applyFiltersAndRender(1);
        }});
      }}

      if (refreshButton) {{
        refreshButton.addEventListener('click', function() {{
          currentSearch = '';
          currentSortKey = null;
          currentSortDirection = 'asc';
          if (searchInput) {{
            searchInput.value = '';
          }}
          allRows.sort(function(a, b) {{
            return parseFloat(a.getAttribute('data-sort-no') || '0') - parseFloat(b.getAttribute('data-sort-no') || '0');
          }});
          updateSortIndicators();
          applyFiltersAndRender(1);
        }});
      }}

      columnToggles.forEach(function(toggle) {{
        toggle.addEventListener('change', function() {{
          applyColumnVisibility();
        }});
      }});

      var exportCurrent = document.getElementById('export-current');
      var exportAll = document.getElementById('export-all');
      if (exportCurrent) {{
        exportCurrent.addEventListener('click', function(event) {{
          event.preventDefault();
          exportRows(false);
        }});
      }}
      if (exportAll) {{
        exportAll.addEventListener('click', function(event) {{
          event.preventDefault();
          exportRows(true);
        }});
      }}

      applyFiltersAndRender(1);
    }})();
  </script>
</body>
</html>"""
    )
