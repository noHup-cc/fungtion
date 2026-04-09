import csv
import json
import random
from collections import OrderedDict
from pathlib import Path

import numpy as np
import pandas as pd
from Bio import Phylo
from Bio.Phylo.TreeConstruction import DistanceMatrix, DistanceTreeConstructor
from sklearn.metrics.pairwise import cosine_similarity


COLOR_PALETTE = [
    "#c23531", "#c8c788", "#61a0a8", "#d48265", "#91c7ae", "#749f83", "#ca8622",
    "#bda29a", "#6e7074", "#c4ccd3", "#546570", "#dd6b66", "#759aa0", "#e69d87",
    "#8dc1a9", "#ea7e53", "#eedd78", "#73a373", "#73b9bc", "#7289ab", "#91ca8c",
    "#f49f42", "#d87c7c", "#919e8b", "#d7ab82", "#efa18d", "#787464", "#cc7e63",
    "#724e58", "#4b565b", "#2ec7c9", "#b6a2de", "#5ab1ef", "#ffb980", "#d87a80",
    "#8d98b3", "#e5cf0d", "#97b552", "#95706d", "#dc69aa", "#07a2a4", "#9a7fd1",
    "#588dd5", "#f5994e", "#c05050", "#59678c", "#c9ab00", "#7eb00a", "#6f5553",
    "#c14089", "#C1232B", "#27727B", "#FCCE10", "#E87C25", "#B5C334", "#FE8463",
    "#9BCA63", "#FAD860", "#F3A43B", "#60C0DD", "#D7504B", "#C6E579", "#F4E001",
    "#F0805A", "#26C0C0", "#E01F54", "#001852", "#f5e8c8", "#b8d2c7", "#c6b38e",
    "#a4d8c2", "#f3d999", "#d3758f", "#dcc392", "#2e4783", "#82b6e9", "#ff6347",
    "#a092f1", "#0a915d", "#eaf889", "#6699FF", "#ff6666", "#3cb371", "#d5b158",
    "#38b6b6", "#c12e34", "#e6b600", "#0098d9", "#2b821d", "#005eaa", "#339ca8",
    "#cda819", "#32a487",
]


def read_fasta_records(fasta_path):
    records = []
    header = None
    seq_lines = []
    with open(fasta_path) as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    records.append((header, "".join(seq_lines)))
                header = line[1:]
                seq_lines = []
            else:
                seq_lines.append(line)
    if header is not None:
        records.append((header, "".join(seq_lines)))
    return records


def safe_stem(value):
    safe = "".join(ch if ch.isalnum() or ch in {"_", "-", "."} else "_" for ch in value)
    safe = safe.strip("._")
    return safe or "query"


def format_seq_name(seq_name):
    return seq_name.replace(",", "").replace(":", "")


def format_para(value):
    if value in {"", "NULL", None}:
        return "-"
    return value


def node_size(value, node_counts):
    if not node_counts:
        return 18
    min_count = min(node_counts.values())
    max_count = max(node_counts.values())
    if min_count == max_count:
        return 18
    normalized = 2 + 15.0 * (value - min_count) / (max_count - min_count)
    return normalized if normalized > 1 else 1 + random.random()


def load_reference_metadata(reference_fasta):
    seq_names = []
    species_list = []
    species_full_list = []
    for header, _sequence in read_fasta_records(reference_fasta):
        seq_name = header.split(" ")[0]
        species_full = header.split(" ", 1)[1] if " " in header else "-"
        species = species_full.split(" ")[0] if species_full != "-" else "-"
        seq_names.append(seq_name)
        species_list.append(species)
        species_full_list.append(species_full)
    return seq_names, species_list, species_full_list


def build_network_json(similarity_tsv, reference_fasta, output_json, threshold=0.9):
    random.seed(1)
    data = OrderedDict()
    data["nodes"] = []
    data["edges"] = []

    sources = []
    targets = []
    node_counts = OrderedDict()
    seen_edges = OrderedDict()

    with open(similarity_tsv) as handle:
        reader = csv.reader(handle, delimiter="\t")
        for row in reader:
            if len(row) < 3:
                continue
            try:
                score = float(row[2])
            except ValueError:
                continue
            if score <= threshold:
                continue
            source = row[0]
            target = row[1]
            sources.append(source)
            targets.append(target)
            node_counts[source] = node_counts.get(source, 0) + 1

    query_nodes = sorted({node for node in sources + targets if "Query" in node})
    for query_node in query_nodes:
        node_counts.setdefault(query_node, 1)

    seq_names, species_list, species_full_list = load_reference_metadata(reference_fasta)
    species_categories = sorted(set(species_list))

    if node_counts:
        x_choices = list(range(0, int(max(node_counts.values()) * len(node_counts.values()) / 2) + 1, max(node_counts.values())))
        y_choices = list(range(100, 100 + int(max(node_counts.values()) * len(node_counts.values()) / 2) + 1, max(node_counts.values())))
    else:
        x_choices = [0]
        y_choices = [100]

    for key, value in node_counts.items():
        if "Query" in key:
            data["nodes"].append({
                "color": "",
                "label": format_seq_name(key),
                "attributes": {},
                "x": random.choice(x_choices),
                "id": format_seq_name(key),
                "y": random.choice(y_choices),
                "size": 18,
                "index": key,
                "speciesfull": "-",
                "species": "-",
                "category": "-",
                "freq": node_size(value, node_counts),
            })
            continue

        species_index = seq_names.index(key)
        species_full = species_full_list[species_index]
        species = species_list[species_index]
        data["nodes"].append({
            "color": COLOR_PALETTE[species_categories.index(species) % len(COLOR_PALETTE)],
            "label": format_seq_name(key),
            "attributes": {},
            "x": random.choice(x_choices),
            "id": format_seq_name(key),
            "y": random.choice(y_choices),
            "size": 18,
            "index": key,
            "speciesfull": format_para(species_full),
            "species": format_para(species),
            "category": species_categories.index(species),
            "freq": node_size(value, node_counts),
        })

    for source, target in zip(sources, targets):
        edge_key = f"{source}_{target}"
        reverse_key = f"{target}_{source}"
        if source == target or edge_key in seen_edges:
            continue
        data["edges"].append({
            "sourceID": source,
            "targetID": target,
            "attributes": {},
            "size": 1,
        })
        seen_edges[edge_key] = 1
        seen_edges[reverse_key] = 1

    with open(output_json, "w") as handle:
        json.dump(data, handle, indent=2)


def compute_cosine_network(reference_cosine_tsv, combined_headers, combined_features, output_tsv):
    result_df = pd.read_csv(reference_cosine_tsv, sep="\t")
    query_id = combined_headers[-1]
    query_vector = combined_features.iloc[-1].to_numpy(dtype=float).reshape(1, -1)
    all_vectors = combined_features.to_numpy(dtype=float)
    similarities = cosine_similarity(all_vectors, query_vector).ravel()

    rows = []
    for target_id, similarity in zip(combined_headers, similarities):
        rows.append({"Query": query_id, "Target": target_id, "cosine_rescaled": similarity})
        if target_id != query_id:
            rows.append({"Query": target_id, "Target": query_id, "cosine_rescaled": similarity})

    result_df = pd.concat([result_df, pd.DataFrame(rows)], ignore_index=True)
    min_value = result_df["cosine_rescaled"].min()
    max_value = result_df["cosine_rescaled"].max()
    if max_value == min_value:
        result_df["cosine_rescaled"] = 1.0
    else:
        result_df["cosine_rescaled"] = (result_df["cosine_rescaled"] - min_value) / (max_value - min_value)
    result_df.to_csv(output_tsv, sep="\t", index=False, header=False)


def compute_nj_tree(reference_distance_tsv, combined_headers, combined_features, output_newick):
    ref_distances = pd.read_csv(reference_distance_tsv, sep="\t")
    query_id = combined_headers[-1]
    query_vector = combined_features.iloc[-1].to_numpy(dtype=float)
    all_vectors = combined_features.to_numpy(dtype=float)
    distances = np.linalg.norm(all_vectors - query_vector, axis=1)

    rows = []
    for target_id, distance in zip(combined_headers, distances):
        rows.append({"Query": query_id, "Target": target_id, "euclidean_distance": distance})
        if target_id != query_id:
            rows.append({"Query": target_id, "Target": query_id, "euclidean_distance": distance})

    all_distances = pd.concat([ref_distances, pd.DataFrame(rows)], ignore_index=True)
    distance_matrix = all_distances.pivot(index="Query", columns="Target", values="euclidean_distance")
    distance_matrix = distance_matrix.reindex(index=combined_headers, columns=combined_headers)
    matrix = [distance_matrix.iloc[i, : i + 1].tolist() for i in range(len(combined_headers))]

    dm = DistanceMatrix(combined_headers, matrix)
    tree = DistanceTreeConstructor().nj(dm)
    Phylo.write([tree], output_newick, "newick")


def generate_visual_outputs(
    fasta_path,
    feature_csv,
    prediction_csv,
    analysis_dir,
    reference_dir,
):
    analysis_dir = Path(analysis_dir)
    reference_dir = Path(reference_dir)
    analysis_dir.mkdir(parents=True, exist_ok=True)

    reference_fasta = reference_dir / "FungalEffector_positive.fasta"
    reference_features_path = reference_dir / "FungalEffector_positive_esm_uniref50.csv"
    reference_cosine_tsv = (
        reference_dir
        / "FungalEffector_positive_similarity_matrix"
        / "FungalEffector_positive_cosine_matrix_esm_uniref50.csv"
    )
    reference_distance_tsv = (
        reference_dir
        / "FungalEffector_positive_similarity_matrix"
        / "FungalEffector_positive_distance_matrix_esm_uniref50.csv"
    )

    records = read_fasta_records(fasta_path)
    features_df = pd.read_csv(feature_csv)
    predictions_df = pd.read_csv(prediction_csv)
    reference_features_df = pd.read_csv(reference_features_path)
    reference_headers = [header.split(" ")[0] for header, _ in read_fasta_records(reference_fasta)]

    if len(records) != len(features_df) or len(records) != len(predictions_df):
        raise ValueError("Input FASTA, extracted features, and predictions are misaligned")

    manifest_rows = []
    for index, ((original_header, sequence), (_, feature_row), prediction_row) in enumerate(
        zip(records, features_df.iterrows(), predictions_df.to_dict("records")),
        start=1,
    ):
        manifest_row = {
            "header": prediction_row["header"],
            "score": prediction_row["score"],
            "decision": prediction_row["decision"],
            "network_json": "",
            "tree_newick": "",
        }
        if prediction_row["decision"] != "yes":
            manifest_rows.append(manifest_row)
            continue

        query_id = f"Query_{index}"
        entry_dir = analysis_dir / f"{index:04d}_{safe_stem(original_header.split(' ')[0])}"
        entry_dir.mkdir(parents=True, exist_ok=True)

        combined_fasta = entry_dir / "tree_and_network.fasta"
        combined_features = entry_dir / "esm_uniref50_tree_and_network.csv"
        cosine_tsv = entry_dir / "cosine_network.tsv"
        network_json = entry_dir / "cosine_network.json"
        tree_newick = entry_dir / "esm1b_tree.nwk"
        metadata_json = entry_dir / "metadata.json"

        with open(combined_fasta, "w") as handle:
            for ref_header, ref_sequence in read_fasta_records(reference_fasta):
                handle.write(f">{ref_header}\n{ref_sequence}\n")
            handle.write(f">{query_id} {original_header}\n{sequence}\n")

        combined_features_df = pd.concat(
            [reference_features_df, pd.DataFrame([feature_row])],
            ignore_index=True,
        )
        combined_features_df.to_csv(combined_features, index=False)

        combined_headers = reference_headers + [query_id]
        compute_cosine_network(reference_cosine_tsv, combined_headers, combined_features_df, cosine_tsv)
        build_network_json(cosine_tsv, reference_fasta, network_json)
        compute_nj_tree(reference_distance_tsv, combined_headers, combined_features_df, tree_newick)

        with open(metadata_json, "w") as handle:
            json.dump(
                {
                    "query_id": query_id,
                    "original_header": original_header,
                    "score": prediction_row["score"],
                    "decision": prediction_row["decision"],
                    "network_json": str(network_json),
                    "tree_newick": str(tree_newick),
                },
                handle,
                indent=2,
            )

        manifest_row["network_json"] = str(network_json)
        manifest_row["tree_newick"] = str(tree_newick)
        manifest_rows.append(manifest_row)

    manifest_path = analysis_dir / "visualization_manifest.csv"
    pd.DataFrame(manifest_rows).to_csv(manifest_path, index=False)
    return manifest_path
