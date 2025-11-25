## Usage

### 1. Extract text from PDFs

Put your PDF files into the `raw_pdfs/` folder, then run:

```bash
python extractor.py
```

This will convert every PDF into page-based JSON files inside:

```
extracted/
```

You only need to do this once per document.

---

### 2. Concept Query Mode (CLI)

Run:

```bash
python cli.py
```

Then just type normal, casual questions or thoughts, for example:

```
> How do technological changes impact social behavior?
```

or

```
> What are the key variables in organizational productivity?
```

The system will return:

* The **top 10 related concepts**
* A short explanation for the **most relevant one**

To exit the CLI:

```
exit
```

---

### 3. Random Text → Telegram

To receive a randomly selected excerpt
(with a short title + simple explanation)
directly on Telegram:

```bash
python cli.py --random
```

This sends you something like a
“daily thought fragment” to read casually.

---

### 4. Help Menu

To see available commands:

```bash
python cli.py --help
```