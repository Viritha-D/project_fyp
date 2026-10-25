1. Install Python 3.13 (or a similar recent version).

2. Open a terminal in the project folder and set up the environment:

   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install sentence-transformers pandas numpy rank_bm25 langdetect scikit-learn
   ```

3. Go into the `run2` folder and start the program:

   ```
   cd run2
   python demo.py
   ```

   The first time, it downloads two small language models, so you need an
   internet connection. Loading takes 10–20 seconds.

4. When you see the `>` prompt, type a description of your problem in plain English
   and press Enter. For example:

   ```
   > I need a strategy for battery charge equalization using a switched capacitor circuit
   ```

5. Read the result:
   - **MATCHED** shows the problem it found, how many papers support it, and the
     algorithms ranked from best to worst.
   - **NO CONFIDENT MATCH** means nothing in the data matched well enough, so it
     does not guess.

6. Type `examples` to see three sample questions, and `quit` to exit.
