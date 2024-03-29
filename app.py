import os, sys
import io, zipfile
import socket
from flask import Flask, make_response, render_template, request, redirect
from flask import request, url_for, send_file, flash
from werkzeug.utils import secure_filename

hostname = socket.gethostname()
ipaddr = socket.gethostbyname(hostname)
print("Your Computer Name is: " + hostname)
print("Your computer IP Address is:" + ipaddr)


app = Flask(__name__)
root = True
app.config["SECRET_KEY"] = "shit is real"
app.config["UPLOADS_FOLDER"] = "Uploads"


def gotoroot():
    os.chdir(os.path.expanduser("~"))


def getitems(path):
    return os.listdir()


def split_folder_file(items):
    items_list = {"folders": [], "files": []}

    for item in items:
        Item = os.path.join(os.getcwd(), item)

        if os.path.isfile(Item):
            items_list["files"].append(item)
        else:
            items_list["folders"].append(item)
    return items_list


@app.route("/up_folder")
def upfolder():
    os.chdir("..")
    return redirect("/receive")


@app.route("/view")
def viewfile():
    path = request.args.get("pathloc")

    if sys.platform == "linux":
        f_path = path.split("\\")
        path, f = f_path[0], f_path[1]
        my_path = os.path.join(path, f)
        
    else:
        print(path)
        my_path = os.path.join(cur_dir,path)

    return send_file(my_path, mimetype="zip")


@app.route("/cd")
def changedir():
    global cur_dir
    c_path = request.args.get("loc")

    if sys.platform == "linux":
        inter = c_path.split("\\")
        c_path = os.path.join(inter[0], inter[1])

    os.chdir(c_path)
    cur_dir = os.getcwd()
    return redirect("/receive")


@app.route("/download_folder/<path:foldername>", methods=["GET", "POST"])
def download_folder(foldername):
    my_path = os.path.join(os.getcwd(), foldername)
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(my_path):
            for file in files:
                zipf.write(os.path.join(root, file))
    memory_file.seek(0)
    # response = make_response(send_file(memory_file, as_attachment=True, mimetype="application/zip"))
    # response.headers["Content-Disposition"] = f"attachment; filename={foldername}.zip"
    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"{foldername}.zp",
    )


@app.route("/download/<path:filename>", methods=["GET", "POST"])
def download(filename):
    my_path = os.path.join(os.getcwd(), filename)
    return send_file(my_path, mimetype="rar", as_attachment=True)


@app.route("/receive")
def receive():
    global root
    if root:
        os.chdir(os.path.expanduser("~"))

    root = False
    return render_template(
        "receive.html",
        path=os.getcwd(),
        item_list=split_folder_file(getitems(os.getcwd())),
    )


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/upload", methods=["POST"])
def upload_file():
    path = os.getcwd() + "\\" + "Uploads"
    if request.method == "POST":
        if "files[]" not in request.files:
            flash("No file Uploaded")
            return redirect(request.url)

        files = request.files.getlist("files[]")
        for file in files:
            filename = secure_filename(file.filename)
            file.save(filename)
            flash("Upload Complete", "info")
    return redirect("/send")


@app.route("/send")
def send():
    return render_template("send.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=False, port=2006)
