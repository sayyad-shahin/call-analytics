import io, json, os
from dotenv import load_dotenv
from flask import Flask, jsonify, send_from_directory, send_file, abort
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import analyzer

load_dotenv()
BASE = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder="static", static_url_path="")
CALLS = {c["id"]: c for c in json.load(open(os.path.join(BASE, "data", "calls.json")))}
CACHE = {}

def get_analysis(cid):
    if cid not in CALLS: abort(404)
    if cid not in CACHE: CACHE[cid] = analyzer.analyze(CALLS[cid])
    return CACHE[cid]

@app.get("/")
def index(): return app.send_static_file("index.html")

@app.get("/api/calls")
def calls():
    return jsonify([{k: v for k, v in c.items() if k != "turns"} for c in CALLS.values()])

@app.get("/api/calls/<int:cid>")
def call(cid):
    if cid not in CALLS: abort(404)
    return jsonify(CALLS[cid])

@app.get("/api/calls/<int:cid>/analysis")
def analysis(cid): return jsonify(get_analysis(cid))

@app.get("/audio/<path:name>")
def audio(name): return send_from_directory(os.path.join(BASE, "audio"), name)

@app.get("/api/calls/<int:cid>/report")
def report(cid):
    c, a = CALLS.get(cid) or abort(404), get_analysis(cid)
    st = getSampleStyleSheet(); buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"Call Report #{cid}", leftMargin=48, rightMargin=48)
    el = [Paragraph(f"Call Analysis Report #{cid}", st["Title"])]
    meta = [["Customer", c["customer"]], ["Company", c["company"]], ["Agent", c["agent"]], ["Date", c["date"]],
            ["Product", c["product"]], ["Sentiment", f"{a['sentiment']} ({a['sentiment_score']})"],
            ["Purchase probability", f"{a['purchase_probability']}%"], ["Engine", a["engine"]]]
    t = Table(meta, colWidths=[130, 360])
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), .4, colors.lightgrey), ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke)]))
    el += [t, Spacer(1, 12), Paragraph("Summary", st["Heading2"]), Paragraph(a["summary"], st["BodyText"])]
    for title, key in [("Key insights", "key_insights"), ("Customer behavior", "customer_behavior"),
                       ("Buying signals", "buying_signals"), ("Objections", "objections")]:
        if a.get(key):
            el.append(Paragraph(title, st["Heading2"]))
            el += [Paragraph("• " + x, st["BodyText"]) for x in a[key]]
    el += [Paragraph("Recommended next action", st["Heading2"]), Paragraph(a["next_action"], st["BodyText"]),
           Paragraph("Transcript", st["Heading2"])]
    el += [Paragraph(f"<b>{s.title()}:</b> {x}", st["BodyText"]) for s, x in c["turns"]]
    doc.build(el); buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"call_{cid}_report.pdf", mimetype="application/pdf")

if __name__ == "__main__":
    app.run(port=5000, debug=True)
