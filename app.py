
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
import boto3
s3 = boto3.resource('s3')
reader = boto3.client('textract')


def list_files():
    files = []
    bucket = s3.Bucket('test-bucket-camilo2')
    for file in bucket.objects.all():
        files.append(s3.Object('test-bucket-camilo2', file.key))
    return files


def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] == 'SELECTED':
                            text += 'X '
    return text


def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}

                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows


def generate_table_csv(table_result, blocks_map, table_index):
    rows = get_rows_columns_map(table_result, blocks_map)

    table_id = 'Table_' + str(table_index)

    # get cells.
    csv = 'Table: {0}\n\n'.format(table_id)

    for row_index, cols in rows.items():

        for col_index, text in cols.items():
            csv += '{}'.format(text) + ","
        csv += '\n'

    csv += '\n\n\n'
    return csv


def get_table_csv_results(image):
    response = reader.analyze_document(
        Document={
            'S3Object': {
                'Bucket': image.bucket_name,
                'Name': image.key,
            }
        },
        FeatureTypes=['TABLES']
    )
    blocks = response['Blocks']

    blocks_map = {}
    table_blocks = []
    for block in blocks:
        blocks_map[block['Id']] = block
        if block['BlockType'] == "TABLE":
            table_blocks.append(block)

    if len(table_blocks) <= 0:
        return "<b> NO Table FOUND </b>"

    csv = ''
    for index, table in enumerate(table_blocks):
        csv += generate_table_csv(table, blocks_map, index + 1)
        csv += '\n\n'

    return csv


def main():
    images = list_files()
    count = 0
    for image in images:
        count = count + 1
        table_csv = get_table_csv_results(image)

        output_file = 'output'+str(count)+'.csv'

        with open(output_file, "wt") as fout:
            fout.write(table_csv)

        s3.upload_file(
            Filename=output_file,
            Bucket='test-bucket-camilo2',
            Key=output_file,
        )


main()
