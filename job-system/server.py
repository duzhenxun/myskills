#!/usr/bin/env python3
import json
import subprocess
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "jobs.json"


def load_jobs():
  return json.loads(DATA_PATH.read_text())


def save_jobs(jobs):
  DATA_PATH.write_text(json.dumps(jobs, ensure_ascii=False, indent=2))


def fetch_job_detail(security_id):
  result = subprocess.run(
    [
      "opencli",
      "boss",
      "detail",
      security_id,
      "--site-session",
      "persistent",
      "--window",
      "foreground",
      "-f",
      "json",
    ],
    capture_output=True,
    text=True,
    cwd=str(BASE_DIR),
  )
  if result.returncode != 0:
    message = result.stderr.strip() or result.stdout.strip() or "opencli boss detail failed"
    raise RuntimeError(message)

  payload = json.loads(result.stdout)
  detail = payload[0] if isinstance(payload, list) and payload else payload
  if not isinstance(detail, dict) or not (detail.get("description") or "").strip():
    raise RuntimeError("detail payload missing description")
  return detail


class JobSystemHandler(SimpleHTTPRequestHandler):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, directory=str(BASE_DIR), **kwargs)

  def _send_json(self, payload, status=200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    self.send_response(status)
    self.send_header("Content-Type", "application/json; charset=utf-8")
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)

  def do_POST(self):
    if self.path != "/api/job-detail":
      self._send_json({"ok": False, "error": "Not found"}, status=404)
      return

    try:
      length = int(self.headers.get("Content-Length", "0"))
      raw = self.rfile.read(length)
      payload = json.loads(raw.decode("utf-8"))
      security_id = (payload.get("security_id") or "").strip()
      if not security_id:
        raise ValueError("security_id is required")

      jobs = load_jobs()
      target = next((job for job in jobs if job.get("security_id") == security_id), None)
      if target is None:
        raise ValueError("job not found")

      if (target.get("description") or "").strip():
        self._send_json({"ok": True, "job": target})
        return

      detail = fetch_job_detail(security_id)
      target["description"] = detail.get("description", "")
      target["welfare"] = detail.get("welfare", target.get("welfare", []))
      target["boss_name"] = detail.get("boss_name", target.get("boss_name", ""))
      target["boss_title"] = detail.get("boss_title", target.get("boss_title", ""))
      target["active_time"] = detail.get("active_time", target.get("active_time", ""))
      target["industry"] = detail.get("industry", target.get("industry", ""))
      target["scale"] = detail.get("scale", target.get("scale", ""))
      target["stage"] = detail.get("stage", target.get("stage", ""))
      target["address"] = detail.get("address", target.get("address", ""))
      target["city"] = detail.get("city", target.get("city", ""))
      target["district"] = detail.get("district", target.get("district", ""))
      target["detail_status"] = "ok"
      save_jobs(jobs)
      self._send_json({"ok": True, "job": target})
    except Exception as exc:
      self._send_json({"ok": False, "error": str(exc)}, status=500)


def main():
  server = ThreadingHTTPServer(("127.0.0.1", 8000), JobSystemHandler)
  print("Serving 职位系统 on http://127.0.0.1:8000")
  server.serve_forever()


if __name__ == "__main__":
  main()
