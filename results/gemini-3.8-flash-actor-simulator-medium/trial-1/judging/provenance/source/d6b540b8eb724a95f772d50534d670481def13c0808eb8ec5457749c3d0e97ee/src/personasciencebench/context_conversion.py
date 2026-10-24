"""Conservative, source-attributed context conversion; no answer synthesis."""
import csv
import io
import json
from pathlib import Path
import re
import zipfile
from personasciencebench.schema import Fact, Provenance
from personasciencebench.adapters.base import sha256

POLICY = "source-context-v2"

def field_facts(text, *, prefix, path, revision, locator, digest, default_kind="context"):
    """Keep native guidance as exact text, classifying advice without paraphrase."""
    if not text.strip():
        return []
    facts = []
    for match in re.finditer(r"[^\n]+", text):
        value = match.group().strip()
        if not value:
            continue
        kind = "optional_advice" if re.search(r"\b(recommend|suggest|consider|can use|could use|tip:|hint:)\b", value, re.I) else default_kind
        facts.append(Fact(id=f"{prefix}.{len(facts)+1}", topic="native_guidance" if kind == "optional_advice" else "study_context",
            text=value, kind=kind, review_status="automated", source=Provenance(
                source_path=path, revision=revision, locator=f"{locator}/chars={match.start()}:{match.end()}", sha256=digest)))
    return facts

def tabular_facts(path, *, prefix, source_path, revision):
    """Inspect permitted input schemas only; never interpret or compute outcomes."""
    suffix = path.suffix.lower()
    records = []
    if suffix in {".csv", ".tsv"}:
        with path.open("rb") as stream:
            sample = stream.read(262144)
        try:
            text = sample.decode("utf-8-sig")
            encoding = "UTF-8 (optional BOM)"
        except UnicodeDecodeError:
            text = sample.decode("latin-1")
            encoding = "Latin-1 decoding; exact source encoding is unspecified"
        delimiter = "\t" if suffix == ".tsv" else ","
        try:
            delimiter = csv.Sniffer().sniff(text[:8192], delimiters=",;\t").delimiter
        except csv.Error:
            pass
        headers = next(csv.reader(io.StringIO(text), delimiter=delimiter), [])
        if headers:
            records.append(("row=1", f"{path.name}: delimiter {delimiter!r}; readable using {encoding}. Header fields (first 80): {json.dumps(headers[:80], ensure_ascii=False)}."))
    elif suffix == ".xlsx":
        # Read workbook XML, avoiding formula execution and a heavy XLSX dependency.
        import xml.etree.ElementTree as ET
        with zipfile.ZipFile(path) as z:
            ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            workbook = ET.fromstring(z.read("xl/workbook.xml"))
            sheets = [x.attrib["name"] for x in workbook.findall("s:sheets/s:sheet", ns)]
            records.append(("xl/workbook.xml/sheets", f"{path.name} worksheet names: {json.dumps(sheets, ensure_ascii=False)}."))
            rows = []
            wanted = set()
            for member in sorted(x for x in z.namelist() if re.fullmatch(r"xl/worksheets/sheet[0-9]+.xml", x)):
                with z.open(member) as stream:
                    for _, elem in ET.iterparse(stream, events=("end",)):
                        if elem.tag.endswith("}row"):
                            cells = []
                            for cell in list(elem)[:80]:
                                v = cell.find("s:v", ns)
                                value = v.text if v is not None else "".join(cell.itertext())
                                shared = cell.attrib.get("t") == "s" and bool(value)
                                if shared:
                                    wanted.add(int(value))
                                cells.append((bool(shared), value or ""))
                            rows.append((member, cells))
                            break
            strings = {}
            if wanted and "xl/sharedStrings.xml" in z.namelist():
                with z.open("xl/sharedStrings.xml") as stream:
                    index = 0
                    for _, elem in ET.iterparse(stream, events=("end",)):
                        if elem.tag.endswith("}si"):
                            if index in wanted:
                                strings[index] = "".join(elem.itertext())
                            elem.clear()
                            if index >= max(wanted):
                                break
                            index += 1
            for member, cells in rows:
                fields = [strings[int(value)] if shared else value for shared, value in cells]
                records.append((member+"/first_row", f"{path.name} ({member}) first-row cells: {json.dumps(fields, ensure_ascii=False)}."))
    digest = sha256(path)
    return [Fact(id=f"{prefix}.{i}", topic="input_schema", text=value, review_status="automated",
        source=Provenance(source_path=source_path, revision=revision, locator=locator, sha256=digest))
        for i,(locator,value) in enumerate(records,1)]
