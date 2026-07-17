"""A small local browser interface for uploading checklist documents."""

from email import policy
from email.parser import BytesParser
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import quote, unquote, urlparse
from uuid import uuid4

from app.config import REPORT_DIR, UPLOAD_DIR
from app.utils import create_folders


MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50 MB
ALLOWED_SUFFIXES = {".pdf", ".docx"}
PROCESSING_LOCK = Lock()


class UploadHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_html(HTTPStatus.OK, self._form())
            return

        if parsed.path.startswith("/reports/"):
            self._download_report(unquote(parsed.path.removeprefix("/reports/")))
            return

        self._send_html(HTTPStatus.NOT_FOUND, self._message("Page not found."))

    def do_POST(self):
        if self.path != "/upload":
            self._send_html(HTTPStatus.NOT_FOUND, self._message("Page not found."))
            return

        try:
            upload = self._read_upload()
            original_name = Path(upload.get_filename() or "").name
            suffix = Path(original_name).suffix.lower()
            if suffix not in ALLOWED_SUFFIXES:
                raise ValueError("Please upload a PDF or DOCX file.")

            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            stored_file = UPLOAD_DIR / f"{uuid4().hex}_{original_name}"
            stored_file.write_bytes(upload.get_payload(decode=True) or b"")

            # The existing image/output folders use fixed names, so process one
            # upload at a time to prevent two reports from sharing files.
            from app.pipeline import Pipeline
            with PROCESSING_LOCK:
                reports = Pipeline().run([stored_file])
            if not reports:
                raise RuntimeError("No report was generated from the uploaded file.")

            report = reports[0]
            link = quote(report.name)
            self._send_html(
                HTTPStatus.OK,
                self._message(
                    "Report generated.",
                    f'<a href="/reports/{link}">Download the Excel report</a>',
                ),
            )
        except (ValueError, RuntimeError) as error:
            self._send_html(HTTPStatus.BAD_REQUEST, self._message(str(error)))
        except Exception:
            self._send_html(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                self._message("The document could not be processed. Check the server console for details."),
            )
            raise

    def _read_upload(self):
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            raise ValueError("Expected a multipart file upload.")

        length = int(self.headers.get("Content-Length", "0"))
        if not 0 < length <= MAX_UPLOAD_SIZE:
            raise ValueError("The file must be between 1 byte and 50 MB.")

        body = self.rfile.read(length)
        message = BytesParser(policy=policy.default).parsebytes(
            f"Content-Type: {content_type}\r\nMIME-Version: 1.0\r\n\r\n".encode() + body
        )
        for part in message.iter_attachments():
            if part.get_param("name", header="content-disposition") == "document":
                return part
        raise ValueError("Choose a document before submitting the form.")

    def _download_report(self, file_name):
        report = (REPORT_DIR / Path(file_name).name).resolve()
        if REPORT_DIR.resolve() not in report.parents or not report.is_file():
            self._send_html(HTTPStatus.NOT_FOUND, self._message("Report not found."))
            return

        data = report.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.send_header("Content-Disposition", f'attachment; filename="{report.name}"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    @staticmethod
    def _form():
        return (
            "<h1>SBM Checklist Counter</h1>"
            "<p>Upload a PDF or DOCX checklist to create an Excel summary.</p>"
            '<form action="/upload" method="post" enctype="multipart/form-data">'
            '<input type="file" name="document" accept=".pdf,.docx" required>'
            '<button type="submit">Generate report</button></form>'
        )

    @staticmethod
    def _message(title, detail=""):
        return f"<h1>{escape(title)}</h1><p>{detail}</p><p><a href=\"/\">Upload another file</a></p>"

    def _send_html(self, status, body):
        content = (
            "<!doctype html><html><head><meta charset=\"utf-8\"><title>SBM Checklist Counter</title>"
            "</head><body>" + body + "</body></html>"
        ).encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def run_server(host="127.0.0.1", port=8000):
    create_folders()
    server = ThreadingHTTPServer((host, port), UploadHandler)
    print(f"Open http://{host}:{port} in your browser. Press Ctrl+C to stop.")
    server.serve_forever()
