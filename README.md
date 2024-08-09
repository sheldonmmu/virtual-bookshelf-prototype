# virtual_bookshelf_flask (0.1)

This repository contains the code for a virtual bookshelf application built using Flask. It relies on the ['New Titles' API](https://www.oclc.org/developer/api/oclc-apis/new-titles-api.en.html) from OCLC.

## Description

The virtual_bookshelf_flask application allows librarians to create a virtual bookshelf full of new titles held at their Library. Users can select the book cover to view the OCLC record about each book.

## Features

- View new books: JSON items are pulled in from the OCLC New Titles API daily.
- See book covers: each book is given a book cover from the Google Books API or a randomly selected colour with the URL assigned by OCN.
- Click on an item: view the OCLC record via hyperlinks from the cover to the record.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/virtual_bookshelf_flask.git
```

2. Navigate to the project directory:

```bash
cd virtual_bookshelf_flask
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Obtain an API key for the OCLC New Titles API and create an .env file in the main dir. Update the hyperlinks to records.

5. Start the application in the terminal:

```bash
python app.py 
```
6. Open your web browser and visit `http://localhost:5000` to access the virtual bookshelf application.

## License

This project is licensed under the [Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International License](https://creativecommons.org/licenses/by-nc-nd/4.0/).

![CC BY-NC-ND 4.0](https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png)

You are free to share, copy, and redistribute the material in any medium or format under the following terms:

- **Attribution**: You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- **NonCommercial**: You may not use the material for commercial purposes.
- **NoDerivatives**: If you remix, transform, or build upon the material, you may not distribute the modified material.

For more details, please visit the [Creative Commons website](https://creativecommons.org/licenses/by-nc-nd/4.0/).
