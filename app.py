from flask import Flask, request, redirect, url_for, render_template, flash
import boto3
import os
import uuid
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", str(uuid.uuid4()))

# Environment variables (required)
DDB_TABLE = os.environ.get("DDB_TABLE")
SERVER_ID = os.environ.get("SERVER_ID")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")

# boto3 client / resource initialization using env creds
session_kwargs = {}
if os.environ.get("AWS_ACCESS_KEY_ID"):
    session_kwargs["aws_access_key_id"] = os.environ.get("AWS_ACCESS_KEY_ID")
if os.environ.get("AWS_SECRET_ACCESS_KEY"):
    session_kwargs["aws_secret_access_key"] = os.environ.get("AWS_SECRET_ACCESS_KEY")
if os.environ.get("AWS_SESSION_TOKEN"):
    session_kwargs["aws_session_token"] = os.environ.get("AWS_SESSION_TOKEN")
if AWS_REGION:
    session_kwargs["region_name"] = AWS_REGION

boto_session = boto3.Session(**session_kwargs)
dynamodb = boto_session.resource("dynamodb")

if not DDB_TABLE:
    raise RuntimeError("Environment variable DDB_TABLE (or DDB_TABLE_NAME) must be set")

table = dynamodb.Table(DDB_TABLE)

# ------------------ Helpers ------------------

def scan_items(filter_q=None, limit=50):
    """Scan DynamoDB table and return list of items. For small datasets only."""
    try:
        if filter_q:
            # naive client-side filter after scan (since we don't have GSI here)
            resp = table.scan(Limit=limit)
            items = resp.get('Items', [])
            qlow = filter_q.lower()
            items = [i for i in items if qlow in (i.get('title','').lower())]
        else:
            resp = table.scan(Limit=limit)
            items = resp.get('Items', [])
        # sort by title for nicer UI
        items.sort(key=lambda x: x.get('title',''))
        return items
    except ClientError as e:
        app.logger.error('DynamoDB scan error: %s', e)
        return []

# ------------------ Routes ------------------

@app.route('/')
def index():
    q = request.args.get('q','')
    items = scan_items(filter_q=q) if q else scan_items()
    return render_template("index.html", items=items, q=q, table_name=SERVER_ID)

@app.route('/create', methods=['POST'])
def create():
    title = request.form.get('title','').strip()
    description = request.form.get('description','').strip()
    if not title:
        flash('Title is required', 'warning')
        return redirect(url_for('index'))

    item_id = str(uuid.uuid4())
    item = {'id': item_id, 'title': title, 'description': description}
    try:
        table.put_item(Item=item)
        flash('Item created successfully', 'success')
    except ClientError as e:
        app.logger.error('Create error: %s', e)
        flash('Failed to create item: ' + str(e), 'danger')
    return redirect(url_for('index'))

@app.route('/edit/<id>')
def edit(id):
    try:
        resp = table.get_item(Key={'id': id})
        item = resp.get('Item')
        if not item:
            flash('Item not found', 'warning')
            return redirect(url_for('index'))
    except ClientError as e:
        app.logger.error('Get error: %s', e)
        flash('Failed to fetch item', 'danger')
        return redirect(url_for('index'))

    return render_template("edit.html", item=item, table_name=SERVER_ID)

@app.route('/update/<id>', methods=['POST'])
def update(id):
    title = request.form.get('title','').strip()
    description = request.form.get('description','').strip()
    if not title:
        flash('Title is required', 'warning')
        return redirect(url_for('edit', id=id))
    try:
        table.update_item(
            Key={'id': id},
            UpdateExpression='SET #t = :t, description = :d',
            ExpressionAttributeNames={'#t': 'title'},
            ExpressionAttributeValues={':t': title, ':d': description}
        )
        flash('Item updated', 'success')
    except ClientError as e:
        app.logger.error('Update error: %s', e)
        flash('Failed to update item', 'danger')
    return redirect(url_for('index'))

@app.route('/delete/<id>', methods=['POST'])
def delete(id):
    try:
        table.delete_item(Key={'id': id})
        flash('Item deleted', 'success')
    except ClientError as e:
        app.logger.error('Delete error: %s', e)
        flash('Failed to delete item', 'danger')
    return redirect(url_for('index'))

# Health check
@app.route('/_health')
def health():
    return {'status': 'ok', 'table': DDB_TABLE}

if __name__ == '__main__':
    # Run dev server on 0.0.0.0:5000
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
