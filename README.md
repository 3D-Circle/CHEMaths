# ChemCalc
**Chem**istry **Calc**ulator for high school level

## Functionality:
### Interactive shell
`main(state)`

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