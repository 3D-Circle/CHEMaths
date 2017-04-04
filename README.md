# CHEMaths
**CHEMaths** (pronounced as *Chemist*) 
is a chemistry calculator for educational uses
suited for high school level chemistry.

## Use Online
**Website**: [Here!](https://chemaths.herokuapp.com/)

## Use Locally
0. If you haven't already, download _python 3.6_ from [Python.org](https://www.python.org/downloads/release/python-360/)
1. Open **Terminal** or **command lines** (depending on your OS)
2. `cd` to the location of this folder  
   for example, if you put the folder on your desktop, type:  
    ```sh
    cd Desktop/CHEMaths
    ```
3. There are three possible ways to use **CHEMaths**: 
   - through an `interactive shell` (_text console_):
   ```sh
   python CHEMaths.py
   ```  
   - through a `local server` (_browser_):
    ```sh
    pip install -r requirements.txt
    python CHEMaths_website.py
    ```
    If the commands are executed successfully, 
    you'll have a message looking like 
    `* Running on http://127.0.0.1:5000/` 
    displayed on your screen.   
    You can then use **CHEMaths** 
    by clicking on that link.
      
    [Flask](http://flask.pocoo.org/)
    is needed to activate the graphical user interface.
    The commands above will install the package for you, 
    and might ask you to enter your password for the installation.  
    Running the program for the first time could take some time
    to set everything up.
  
## Functionality (_CHEMaths.py_):
### Interactive shell
`lauch_shell(state)`  
where the shell is activated if state evaluates to `True`  
and prints out debugging information otherwise

- interactive shell
- example (user input is *H2 + O2 -> H2O*):

	
		===START===
		Enter a formula or equation to balance (enter if you don't): H2 + O2 -> H2O
		2 H2 +  O2 -> 2 H2O
		===END: 0.000621 seconds===

### process chemical formula
`process_formula(str_in)`  

- Process string formula to dictionary containing atom and corresponding quantity.  
- i.e. process_formula('(KI)3O') = {'K': 3, 'I': 3, 'O': 1}

### calculate relative formula mass (Mr)
`mr_calc(dict_in)`  

- Calculate relative formula mass for dictionary input processed by function process_formula.

### calculate mole / mass 
`smart_calculate(dict_in, details)`

- Smart handling input details (i.e. mole, mass, etc.) and printing out available information

### determine empirical formula
`get_ratio(dict_in)`

- Calculate empirical formula of a compound given its atoms' mass or percentage of mass in the compound.
- *only accurate to an extent due to floating point handling*

### determine oxidation number
`calculate_oxidation(dict_in)`

- Return the oxidation number of all elements in the input dictionary  
'Bear in mind: this is merely a model'  - Mr. Osler

### balance chemical equation
`process_and_balance_equation(equation)`

- processes input string chemical equation into a matrix and return the least significant integer solution to that matrix which is the balanced equation

### Alkane modelling
`Alkane(size)`

#### `self.__init__()`
- Initialize an alkane according to the input size

#### `self.name`
stores the molecule's name based on the input size

#### `self.__str__()`
returns a 2D plain text illustration of the molecule

- Return lewis structure of the alkane

#### `self.calculate_isomer_numbers()`
- Return the number of total possible configurations of the isomer of the alkane

## To do:
### Visual
- [x] grid
- [ ] tooltip for modes
- [ ] move out of sub / sup box when alphabet is entered 
- [ ] render results based on url
- [ ] css enhancement for input fields
- [ ] enable(expand) / disable(collapse) input fields based on mode
- [ ] Sync mode-specific input fields with main input field

### Server
- [ ] Latex parser
- [x] Deploy to Heroku

### Core
- [ ] fix issues caused by float point precision (while determining empirical formula)
