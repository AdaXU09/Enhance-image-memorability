DATA = r'''
1|no|no|no|yes|noodle|1|100|100||simple|angled|bright||Pasta with shrimp and radish slivers fills a white plate.|shrimp pasta with radish
2|no|yes|no|yes|dessert|1|80|60||medium|angled|bright||An ice cream sundae sits in a waffle bowl with chocolate sauce.|waffle bowl chocolate sundae
3|no|yes|no|yes|rice|1|100|100|cropped at edge|simple|angled|medium||A large rice platter carries grilled meats and falafel.|mixed grill falafel rice platter
4|no|no|no|yes|burger|1|100|60||simple|side|bright||A sliced rye sandwich contains layers of cured meat.|cured meat rye sandwich
5|no|no|no|yes|dessert|1|100|90|cropped at edge|simple|angled|bright||Pillowy fried pastries are covered in powdered sugar.|powdered beignets
6|no|yes|no|yes|burger|2|100|80|cropped at edge|simple|angled|medium||A grilled cheese sandwich accompanies a cup of tomato soup.|grilled cheese sandwich
7|no|no|no|yes|dessert|1|100|90|cropped at edge|simple|angled|medium||A chocolate tart slice sits beside peanuts and cream.|chocolate peanut tart
8|no|no|no|yes|fried|3plus|90|40||medium|side|dark||Fried calamari and vegetables are piled on a rectangular plate.|fried calamari vegetables
9|no|yes|no|yes|dessert|1|80|50||complex|angled|bright||A popcorn dessert is served in a decorated snack box.|popcorn sundae
10|no|no|no|yes|other|2|80|40||medium|angled|medium||Roasted cauliflower is topped with herbs and crumbly cheese.|roasted cauliflower herbs cheese
11|yes|yes|no|yes|fried|1|50|50||complex|side|medium||A hand holds a bitten falafel in front of a food stand.|bitten falafel
12|no|no|no|yes|other|1|100|100|cropped at edge|simple|angled|bright||Pink raw fish pieces are arranged with carrots and delicate herbs.|raw tuna carrot dish
'''
DATA += r'''
13|no|no|no|yes|grill|3plus|100|80|cropped at edge|medium|angled|medium||Grilled meat strips share a plate with squash and coleslaw.|grilled meat squash coleslaw
14|no|no|no|yes|pizza|1|90|100|cropped at edge|simple|top|bright||A round pizza has white cheese and crumbled bacon.|white cheese bacon pizza
15|no|no|no|yes|salad|1|90|80||simple|angled|bright||Sliced steak rests over a salad with jalapeno slices.|steak jalapeno salad
16|no|no|no|yes|other|1|100|100|cropped at edge|simple|angled|medium||Glazed meat strips are stir-fried with green peppers.|green pepper meat stir fry
17|yes|no|no|yes|salad|3plus|40|30|main dish ambiguous|complex|angled|medium||A diner fills a bowl at a buffet with multiple food trays.|buffet salad bowl
18|no|no|no|yes|grill|2|100|70|cropped at edge|simple|angled|bright||Two browned stuffed chicken pieces sit on a white plate.|cheese stuffed grilled chicken
19|no|yes|no|yes|burger|1|80|90||simple|side|medium||A cheeseburger uses tomato halves as buns with fried toppings.|tomato bun cheeseburger
20|no|no|no|yes|fried|1|70|60||simple|side|bright||Curly fries are heaped with bacon and cheese sauce.|bacon cheese curly fries
21|no|no|no|yes|pizza|1|100|90|cropped at edge|simple|angled|medium||Two large cheese pizza slices sit on a paper plate.|plain cheese pizza slices
22|no|no|no|yes|noodle|1|100|100|cropped at edge|simple|top|bright||Thin pasta is coated with creamy sauce and chopped herbs.|creamy thin pasta
23|no|yes|no|yes|burger|1|90|60||complex|angled|bright||A folded taco contains ground meat lettuce and shredded cheese.|beef lettuce cheese taco
24|no|no|no|yes|salad|1|100|100||simple|top|bright||A chopped salad contains yellow pepper rings tomatoes and white cheese.|pepper ring feta salad
'''
DATA += r'''
25|no|yes|no|yes|salad|3plus|90|50||complex|angled|medium||Tomato mozzarella and basil slices form a caprese salad.|caprese tomato mozzarella salad
26|no|no|no|yes|fried|2|50|90||simple|angled|medium||Golden croquettes are arranged in a line over orange sauce.|croquettes orange sauce
27|no|no|no|yes|burger|3plus|80|80|cropped at edge|medium|angled|bright||A roast beef sandwich has melted white cheese and dipping jus.|roast beef cheese dip sandwich
28|no|no|no|yes|grill|1|60|90|cropped at edge|medium|angled|medium||A heavily seasoned split chicken cooks on a grill.|grilled split chicken
29|yes|no|no|yes|fried|1|100|70|cropped at edge|complex|side|medium||A broad tray of nachos is covered in beef and melted cheese.|beef cheese nachos
30|yes|yes|no|yes|pizza|3plus|60|40|main dish ambiguous|complex|angled|medium||Several different pizzas fill a shop display case.|pizza display assortment
31|no|no|no|yes|burger|2|100|100|cropped at edge|simple|angled|bright||Small meat tacos are topped with white cheese and diced peppers.|meat white cheese tacos
32|no|no|no|yes|grill|1|100|100|cropped at edge|simple|angled|medium||Two steaks are topped with white sauce beside Brussels sprouts.|steak white sauce Brussels sprouts
33|no|yes|no|yes|fried|3plus|100|50|cropped at edge|complex|angled|dark||Golden fried dough bites sit in a basket with red sauce.|fried dough bites red sauce
34|yes|yes|no|yes|other|3plus|30|30|main dish ambiguous|complex|angled|medium||Two diners sit at a table of seafood and small dishes.|dining table seafood assortment
35|no|no|no|yes|burger|3plus|100|70|cropped at edge|medium|angled|bright||A toasted meat sandwich is served with chips and dipping jus.|toasted meat sandwich chips jus
36|no|no|no|yes|other|1|80|60||simple|side|bright||Four golden biscuits are stacked on a red cake stand.|stacked plain biscuits
'''
DATA += r'''
37|no|no|no|yes|dessert|2|80|90|main dish ambiguous|simple|angled|medium||Powdered beignets sit beside a powdered funnel cake.|powdered beignets
38|no|no|no|yes|rice|1|100|100|cropped at edge|simple|angled|bright||Sushi rolls contain fish and bright orange roe.|fish orange roe sushi
39|no|no|no|yes|other|1|100|100|cropped at edge|simple|top|medium||Crisp bites are topped with cheese radish slices and mint.|cheese radish mint bites
40|no|no|no|yes|soup|2|70|90||simple|angled|bright||A red vegetable stew contains potatoes carrots and zucchini.|red potato vegetable stew
41|no|no|no|yes|burger|1|100|100|cropped at edge|simple|angled|medium||Two vegetable wrap halves reveal carrot and leafy green fillings.|carrot greens vegetable wrap
42|no|no|no|yes|grill|3plus|80|80|cropped at edge|complex|angled|medium||Sliced duck breast is served with asparagus and red sauce.|duck breast asparagus red sauce
43|no|no|no|yes|rice|1|100|80|cropped at edge|simple|side|medium||Four sushi rolls have avocado mango and red roe toppings.|mango avocado sushi rolls
44|no|no|no|yes|other|1|100|100|cropped at edge|medium|angled|medium||Baked oysters with green herb crumbs accompany sliced bread.|herb baked oysters
45|no|no|no|yes|dessert|1|100|70|cropped at edge|simple|angled|bright||A chocolate covered rolled cake slice has white cream dollops.|chocolate coated rolled cake
46|no|no|no|yes|other|1|100|100|cropped at edge|simple|angled|bright||A round egg dish is topped with spinach tomato sauce and cheese.|spinach tomato cheese frittata
47|no|no|no|yes|other|1|100|100|cropped at edge|simple|angled|bright||Glazed meatloaf slices accompany mashed potatoes and mixed vegetables.|glazed meatloaf vegetables mash
48|no|no|no|yes|salad|2|60|80||simple|top|medium||Chopped chicken salad contains cucumber tomato and white cheese.|chicken cucumber feta salad
'''
DATA += r'''
49|no|no|no|yes|fried|1|100|100|cropped at edge|simple|angled|bright||Tortilla chips carry chicken peppers onions and melted cheese.|chicken pepper cheese nachos
50|no|yes|no|yes|other|1|100|100|cropped at edge|simple|angled|medium||A cheese board includes grapes almonds and dried cranberries.|cheese grapes almond board
51|yes|yes|no|yes|dessert|2|50|40|main dish ambiguous|complex|angled|medium||Two people display plates of pastries and cupcakes.|pastry cupcake assortment
52|no|no|no|yes|noodle|1|100|100|cropped at edge|simple|angled|bright||Filled pasta is baked in tomato sauce under melted cheese.|baked filled pasta tomato cheese
53|no|no|no|yes|other|3plus|100|80|cropped at edge|medium|side|bright||Fried eggs top a vegetable and sausage breakfast skillet.|egg sausage vegetable skillet
54|no|no|no|yes|dessert|2|100|90|cropped at edge|simple|top|medium||Pancakes accompany a fried egg and strips of bacon.|pancakes egg bacon
55|no|yes|no|yes|fried|2|100|90|cropped at edge|medium|angled|medium||Breaded fried chicken strips surround red dipping sauce.|fried chicken strips red sauce
56|no|no|no|yes|salad|3plus|100|90||medium|angled|medium||Ground meat and lettuce are served with salsa and shredded cheese.|ground meat lettuce salad
57|no|no|no|yes|dessert|1|90|100|cropped at edge|medium|top|bright||A lemon tart has a ring of toasted meringue swirls.|lemon meringue tart
58|yes|yes|no|yes|drink|3plus|40|50||complex|angled|bright||A hand holds a green smoothie beside other drinks and breakfast dishes.|green smoothie
59|no|no|no|yes|dessert|1|90|100|cropped at edge|simple|angled|bright||A basket contains pink yellow and brown concha sweet breads.|multicolored concha breads
60|no|yes|no|yes|drink|1|70|80||simple|top|bright||A dark red iced drink is garnished with mint and berries.|red berry mint iced drink
'''
DATA += r'''
61|yes|no|no|yes|dessert|3plus|40|80||complex|angled|medium||A tiered white celebration cake is decorated with red icing.|tiered white red celebration cake
62|no|no|no|yes|pizza|3plus|80|60|cropped at edge|complex|angled|medium||A pepperoni pizza sits in front of other pizzas and a drink.|pepperoni pizza
63|no|no|no|yes|fried|2|100|80|cropped at edge|simple|angled|bright||Battered fish and shrimp are served with fries and corn.|fried fish shrimp platter
64|no|no|no|yes|grill|1|100|100|cropped at edge|simple|angled|bright||A white fish fillet has a dark crumb crust and leafy vegetables.|crumb crust white fish
65|yes|no|no|yes|burger|1|90|100|cropped at edge|simple|side|medium||A long sandwich contains fried shrimp lettuce and tomato.|fried shrimp po boy
66|no|yes|no|yes|dessert|3plus|30|30|main dish ambiguous|complex|angled|medium||Decorated layer cakes fill a bakery display.|bakery layer cake display
67|no|no|no|yes|noodle|1|90|90|cropped at edge|simple|angled|dark||Ramen in dark broth has pork egg halves and seaweed.|pork egg dark broth ramen
68|no|no|no|yes|dessert|3plus|90|80|cropped at edge|complex|angled|medium||French toast is topped with strawberries banana and powdered sugar.|strawberry banana French toast
69|no|no|no|yes|other|1|100|100|cropped at edge|simple|angled|medium||Soft tofu and dark mushrooms sit in a red brown sauce.|tofu wood ear mushroom stew
70|no|no|no|yes|noodle|1|100|100|cropped at edge|simple|angled|bright||Spaghetti with meat sauce is topped with melted white cheese.|spaghetti meat sauce white cheese
71|yes|no|no|yes|salad|1|90|90|cropped at edge|simple|angled|medium||A salad is topped with fried fish crunchy grains and creamy dressing.|fried fish crunchy grain salad
72|yes|no|no|yes|salad|1|70|60||simple|angled|bright||Chicken salad includes avocado bacon tomato and shredded cheese.|chicken avocado bacon salad
'''
DATA += r'''
73|yes|yes|no|yes|rice|3plus|100|60|cropped at edge|complex|angled|dark||A plate of reddish fried rice sits on a crowded dining table.|red fried rice
74|no|no|no|yes|pizza|1|100|100|cropped at edge|simple|top|medium||A charred crust pizza carries cherry tomatoes and white cheese.|cherry tomato white cheese pizza
75|no|no|no|yes|rice|1|90|100||simple|angled|dark||Glazed eel tops rice with shredded vegetables and lemon slices.|eel rice lemon bowl
76|no|no|no|yes|other|3plus|40|50|main dish ambiguous|complex|top|medium||A table holds fish salads dips and several other dishes.|mixed meal table
77|no|no|no|yes|dessert|3plus|80|70||medium|side|bright||Stacks of cookies have colorful candy pieces baked into them.|colorful candy cookies
78|yes|no|no|yes|fried|3plus|70|60|main dish ambiguous|complex|angled|dark||Potato chips and dipping sauces sit beside a salad bowl.|chips dipping sauces
79|no|yes|no|yes|burger|2|100|60|cropped at edge|simple|side|medium||A wheat roll sandwich contains tuna tomato and red onion.|tuna tomato red onion sandwich
80|no|no|no|yes|dessert|1|100|100|cropped at edge|simple|top|medium||Four assorted cupcakes have chocolate cherry and marshmallow toppings.|assorted four cupcakes
81|no|no|no|yes|burger|2|100|90|cropped at edge|medium|angled|medium||Three fish sliders accompany fries and a small sauce cup.|fish sliders fries
82|no|no|no|yes|salad|3plus|100|70|cropped at edge|complex|angled|medium||A lettuce wedge is topped with cheese bacon and chopped vegetables.|cheese bacon wedge salad
83|no|no|no|yes|other|2|40|40||medium|angled|medium||A small skillet of browned spinach dip accompanies flatbread wedges.|baked spinach dip
84|yes|no|no|no|other|1|30|50|food identity unclear|medium|angled|medium||A hand holds a small dark fragment above a bowl.|unidentified dark fragment
'''
DATA += r'''
85|no|no|no|yes|burger|1|90|100|cropped at edge|simple|angled|bright||Rolled sandwich slices contain pale meat spinach and red pepper.|spinach pepper meat sandwich rolls
86|no|no|no|yes|fried|2|100|100||simple|top|medium||A breaded stuffed bite is cut open beside red dipping sauce.|stuffed breaded bite red sauce
87|no|no|no|yes|other|3plus|100|90|cropped at edge|complex|angled|medium||A baked potato is loaded with meat cheese bacon and green onions.|meat cheese bacon baked potato
88|yes|yes|no|yes|grill|3plus|50|30||complex|angled|dark||Bacon wrapped stuffed peppers sit beside chips salsa and beer.|bacon wrapped stuffed peppers
89|no|no|no|yes|grill|2|100|100|cropped at edge|simple|top|medium||A whole red spiced grilled fish accompanies naan and green sauce.|whole red spiced grilled fish
90|no|no|no|yes|fried|2|100|90|cropped at edge|simple|side|medium||Thin battered fried strips are piled beside creamy orange sauce.|battered fried strips orange sauce
91|no|no|no|yes|grill|1|70|90||medium|angled|medium||A stone bowl holds grilled beef chicken shrimp and cactus.|mixed grill stone bowl
92|no|yes|no|yes|fried|2|100|80|cropped at edge|medium|angled|bright||Small breaded fried bites accompany yellow dipping sauce.|breaded fried bites yellow sauce
93|no|no|no|yes|grill|1|90|50||simple|side|dark||A grilled steak accompanies green beans and a loaded baked potato.|steak green beans baked potato
94|no|yes|no|yes|burger|3plus|100|100|cropped at edge|medium|angled|bright||A cheeseburger cut in half sits beside thick fries.|halved cheeseburger thick fries
95|no|yes|no|yes|burger|3plus|60|40|main dish ambiguous|complex|angled|bright||Several burritos share a table with chips sauce and cinnamon twists.|assorted burritos chips
96|no|yes|no|yes|pizza|1|100|60||medium|angled|bright||A rectangular pizza has tomato sauce white cheese and basil.|rectangular margherita pizza
'''
DATA += r'''
97|no|yes|no|yes|burger|1|80|70||complex|angled|bright||A hard shell taco contains beef lettuce and shredded cheese.|beef lettuce cheese taco
98|no|no|no|yes|soup|3plus|90|100|cropped at edge|medium|top|medium||A red seafood soup contains shrimp fish and chopped green onion.|red seafood soup
99|no|no|no|yes|fried|1|100|90|cropped at edge|simple|side|medium||A fried chicken piece is coated in thick red sauce.|red sauced fried chicken
100|no|yes|no|yes|burger|1|90|100|cropped at edge|simple|side|medium||A thick pale chicken burger has lettuce and red onion.|chicken lettuce red onion burger
101|no|yes|no|yes|burger|1|70|50||simple|side|medium||A fried chicken sandwich includes pickles and creamy sauce.|fried chicken pickle sandwich
102|no|no|no|yes|burger|1|100|100|cropped at edge|simple|angled|medium||Four fried fish sliders have glossy buns and lettuce.|fish sliders lettuce
103|no|no|no|yes|other|3plus|100|60|cropped at edge|medium|angled|medium||A lobster shell is filled with creamy pasta and crumb topping.|lobster shell macaroni cheese
104|no|no|no|yes|burger|3plus|100|100|cropped at edge|complex|angled|medium||Two beef sandwich halves accompany onion rings and dipping jus.|beef sandwich onion rings jus
105|no|no|no|yes|fried|1|100|100|cropped at edge|simple|angled|bright||Two crab cakes have tan sauce beside mashed potatoes and greens.|crab cakes mash greens
106|yes|no|no|yes|dessert|1|70|50||simple|side|medium||A tiramisu slice is served with a strawberry and biscuit.|tiramisu strawberry biscuit
107|yes|yes|no|yes|burger|3plus|60|50|cropped at edge|complex|angled|medium||A pulled meat burger accompanies a small macaroni dish.|pulled meat burger
108|no|no|no|yes|fried|2|100|100|cropped at edge|simple|angled|medium||Tater tots are loaded with shredded meat and slaw.|pulled meat slaw tater tots
'''
DATA += r'''
109|no|yes|no|yes|rice|1|100|100|cropped at edge|medium|angled|bright||Shrimp tempura sushi is drizzled with brown sauce and creamy topping.|shrimp tempura sushi creamy sauce
110|no|no|no|yes|grill|3plus|90|60|cropped at edge|complex|angled|medium||Sliced steak is served with thin fried onions and green beans.|steak thin fried onions
111|no|no|no|yes|burger|2|100|80|cropped at edge|simple|angled|bright||A soft taco holds black beans lettuce and shredded cheese.|black bean lettuce taco
112|no|yes|no|yes|salad|1|100|100|cropped at edge|simple|angled|bright||A grilled salmon fillet tops a Caesar style green salad.|salmon Caesar salad
113|no|no|yes|yes|dessert|3plus|100|50|main dish ambiguous|medium|top|medium||A collage shows crumb topped pastries and different breads.|pastry bread collage
114|yes|no|no|yes|noodle|2|100|60|cropped at edge|medium|angled|medium||Dark ribbon pasta is mixed with mushrooms and creamy sauce.|dark mushroom ribbon pasta
115|no|yes|no|yes|rice|1|100|100||simple|top|medium||A mound of chicken rice accompanies plantains and salad.|chicken rice plantains salad
116|no|no|no|yes|pizza|1|100|100|cropped at edge|simple|angled|medium||A thin pizza is topped with white cheese and green pepper strips.|green pepper white cheese pizza
117|yes|yes|no|yes|other|3plus|60|40|main dish ambiguous|complex|angled|medium||Small shared plates include savory toast and baked seafood bites.|shared small plate assortment
118|no|no|no|yes|grill|1|100|80||simple|angled|medium||Several cooked shrimp sit in a shallow bowl with seasoned oil.|shrimp seasoned oil
119|no|no|no|yes|other|2|100|100|cropped at edge|medium|angled|medium||Shrimp tofu and peppers are coated in a glossy dark sauce.|shrimp tofu pepper stir fry
120|no|no|no|yes|burger|3plus|80|30|main dish ambiguous|complex|angled|medium||Rows of tacos sit beside bowls of fried bites and soup.|mixed taco feast
'''
DATA += r'''
121|yes|yes|no|yes|other|3plus|100|80|cropped at edge|complex|angled|medium||An omelet comes with toast and a bowl of pale grits.|omelet toast grits
122|no|yes|no|yes|fried|2|90|60|cropped at edge|medium|angled|medium||Tortilla chips accompany a cup of pale cheese dip.|tortilla chips cheese dip
123|no|yes|no|yes|rice|3plus|100|50||medium|side|medium||A foil rice bowl has salsa greens and shredded white cheese.|salsa cheese rice bowl
124|no|yes|no|yes|rice|1|70|80||medium|top|medium||A compact mound of brown fried rice is dotted with green peas.|brown pea fried rice
125|no|no|no|yes|pizza|1|90|90||simple|top|medium||A pepperoni pizza has a ring of round stuffed crust pieces.|pepperoni stuffed bite crust pizza
126|no|no|no|yes|pizza|1|100|100|cropped at edge|simple|angled|medium||A thick pizza is topped with sausage olives and green peppers.|sausage olive green pepper pizza
127|yes|no|no|yes|grill|1|100|40|cropped at edge|simple|side|bright||A seared white fish fillet sits over puree with crisp vegetable strands.|white fish puree crisp strands
128|yes|no|no|yes|dessert|1|60|60||simple|side|bright||A hand holds a bitten flaky glazed pastry.|bitten glazed flaky pastry
129|no|no|no|yes|drink|2|20|40|main dish ambiguous|medium|top|bright||Green and red smoothies are surrounded by fruit and leafy greens.|green red fruit smoothies
130|no|yes|no|yes|burger|3plus|100|50|cropped at edge|complex|angled|bright||Cheesy grilled quesadilla pieces sit with wrapped food and a blue drink.|grilled cheese quesadilla
131|no|yes|no|yes|rice|3plus|40|40|main dish ambiguous|complex|angled|bright||A rice bowl and burritos share a table with chips and guacamole.|rice burrito meal assortment
132|no|yes|no|yes|grill|1|100|100|cropped at edge|simple|angled|medium||A grilled meat skewer accompanies rice and a diced vegetable salad.|meat skewer rice salad
'''
DATA += r'''
133|yes|no|no|yes|burger|2|100|50|cropped at edge|simple|side|medium||A platter holds many small burgers with lettuce and tomato.|mini lettuce tomato burgers
134|no|no|no|yes|grill|3plus|90|100|cropped at edge|complex|top|medium||A charred steak accompanies pale fries and ketchup.|charred steak fries ketchup
135|no|no|no|yes|salad|2|70|50||complex|angled|bright||A chopped steak salad includes avocado egg bacon and yellow cheese.|steak avocado egg salad
136|no|no|no|yes|grill|1|90|90|cropped at edge|medium|angled|medium||Seared scallops sit in dark sauce with white beans and greens.|scallops white bean greens
137|no|no|no|yes|dessert|1|100|70|cropped at edge|simple|side|medium||Bread pudding is topped with vanilla ice cream and caramel.|caramel ice cream bread pudding
138|no|yes|no|yes|other|3plus|50|30|main dish ambiguous|complex|angled|medium||A promotional meal spread contains pita wraps salad and dips.|pita salad dip spread
139|no|yes|no|yes|burger|2|80|70||simple|angled|medium||A chicken Caesar wrap reveals lettuce croutons and shaved cheese.|chicken Caesar wrap
140|no|no|no|yes|fried|3plus|100|90|cropped at edge|medium|angled|medium||Golden egg rolls are served with red and creamy dipping sauces.|golden egg rolls
141|no|yes|no|yes|rice|1|100|100|cropped at edge|simple|angled|bright||A combo plate has fried rice sliced chicken and a vegetable meat stir fry.|fried rice chicken stir fry combo
142|no|no|no|yes|burger|1|80|40||simple|side|medium||A biscuit sandwich contains folded egg bacon and yellow cheese.|bacon egg cheese biscuit
143|no|no|no|yes|burger|1|100|90|cropped at edge|simple|side|medium||A thick burger is piled with shredded lettuce tomato and onion beside fries.|shredded lettuce onion thick burger
144|no|yes|no|yes|burger|3plus|100|70||complex|side|medium||A bacon cheeseburger sits beside thick fries in a tall container.|bacon cheeseburger
'''
DATA += r'''
145|no|no|no|yes|drink|1|40|90||simple|side|medium||A mint green milkshake is crowned with cream sprinkles and cookies.|mint sprinkle cookie milkshake
146|yes|no|no|yes|dessert|1|90|30||simple|side|bright||A hand supports a box of six colorful macarons.|six colorful macarons
147|no|no|no|yes|burger|1|100|100|cropped at edge|simple|side|bright||Two salmon topped toast pieces have creamy sauce and lemon garnish.|salmon lemon toast
148|no|no|no|yes|grill|1|100|100|cropped at edge|simple|angled|bright||Pale poached chicken and red roast duck slices share a plate.|poached chicken roast duck platter
149|no|yes|no|yes|dessert|1|100|100|cropped at edge|simple|angled|bright||A banana split is covered in whipped cream and cherries.|banana split whipped cream
150|yes|yes|no|yes|fried|3plus|70|60||complex|side|medium||Tongs lift an egg roll above a stack of golden egg rolls.|golden egg rolls
151|no|no|no|yes|fried|2|90|80||medium|angled|medium||A breaded cutlet accompanies broccoli and orange mashed potatoes.|breaded cutlet broccoli sweet mash
152|yes|no|no|yes|other|2|100|100|cropped at edge|medium|angled|medium||A buffet tray is heaped with crab legs and shrimp.|crab legs shrimp buffet
153|no|no|no|yes|burger|3plus|100|60|cropped at edge|medium|side|bright||A double cheeseburger with red onion accompanies fries.|double cheeseburger red onion
154|no|no|no|yes|other|1|60|70||simple|angled|medium||An oval casserole has a golden crumb crust and red chili garnish.|golden crumb casserole
155|no|no|no|yes|rice|1|100|100|cropped at edge|simple|angled|medium||Sushi rolls have creamy orange sauce roe and a carved carrot.|creamy orange sauce sushi rolls
156|no|no|no|yes|other|1|100|80|cropped at edge|simple|angled|medium||Sashimi slices include salmon white fish and scallops with orange roe.|salmon white fish scallop sashimi
'''
DATA += r'''
157|no|no|no|yes|fried|1|100|100|cropped at edge|simple|angled|medium||Fried chicken pieces are coated in orange red glaze with orange wedges.|orange glazed chicken
158|no|no|no|yes|noodle|1|100|100|cropped at edge|simple|side|bright||A thick lasagna slice shows layers of meat sauce and white cheese.|meat cheese lasagna
159|no|no|no|yes|pizza|1|100|100|cropped at edge|simple|angled|medium||Two cheese pizza slices have small basil leaves.|cheese basil pizza slices
160|no|no|no|yes|rice|1|100|90|cropped at edge|simple|top|medium||A rice bowl is topped with avocado seaweed and creamy orange sauce.|avocado seaweed rice bowl
161|no|no|no|yes|rice|1|80|70||medium|angled|bright||A divided bento box contains white rice fish salad and small sides.|fish white rice bento
162|no|no|no|yes|soup|1|90|90||simple|angled|medium||A spicy red stew contains tofu pale slices peanuts and green onion.|spicy tofu peanut stew
163|no|no|no|yes|noodle|1|100|100|cropped at edge|simple|top|medium||Four uncooked ravioli lie dusted with flour.|uncooked square ravioli
164|no|yes|no|yes|fried|3plus|40|40|main dish ambiguous|complex|top|medium||Several trays contain plain and glazed fried chicken.|mixed fried chicken trays
165|no|no|no|yes|dessert|2|100|100|cropped at edge|simple|angled|bright||A cluster of glossy sweet buns is studded with dark raisins.|raisin sweet buns
166|no|no|no|yes|burger|2|100|100|cropped at edge|simple|angled|bright||An everything bagel sandwich contains egg spinach and tomato.|egg spinach tomato bagel
167|no|no|no|yes|rice|1|100|100|cropped at edge|simple|angled|medium||A long sushi board includes tuna jalapeno and tempura topped rolls.|tuna jalapeno tempura sushi board
168|no|no|no|yes|burger|2|100|90|cropped at edge|simple|top|medium||Assorted sesame poppy and plain bagels accompany cream cheese.|assorted bagels cream cheese
'''
DATA += r'''
169|no|yes|no|yes|fried|1|50|70||simple|side|dark||Seasoned fries stand in a checked paper carton.|seasoned fries carton
170|no|no|no|yes|dessert|1|80|100|cropped at edge|complex|top|medium||A large cookie dessert is topped with ice cream and caramel drizzle.|cookie ice cream caramel dessert
171|no|no|no|yes|grill|1|100|100|cropped at edge|simple|top|bright||A divided platter holds cooked shrimp and greens around lemon wedges.|shrimp greens divided platter
172|no|no|no|yes|burger|1|100|80||simple|side|bright||A bagel sandwich contains sliced roast beef cheese and red onion.|roast beef cheese bagel
173|no|no|no|yes|other|2|80|80||medium|angled|medium||A small bowl contains mushrooms olives and pale vegetable pieces.|mushroom olive vegetable bowl
174|yes|no|no|yes|burger|1|60|90||simple|side|bright||A hand holds a split roll stuffed with chopped steak onions and cheese.|steak onion cheese roll
175|no|yes|no|yes|grill|1|100|100|cropped at edge|simple|angled|bright||A steak breakfast includes fried eggs toast and a round hash brown.|steak egg hash brown breakfast
176|no|no|no|yes|fried|1|100|100|cropped at edge|simple|top|medium||Chicken wings in a takeout box are coated with dark glossy sauce.|dark glazed chicken wings
177|no|yes|no|yes|other|1|70|80||simple|angled|bright||Seasoned edamame pods fill a black bowl.|seasoned edamame
178|no|yes|no|yes|other|2|90|80|cropped at edge|complex|angled|medium||Creamy macaroni and cheese is sprinkled with herbs and crumbs.|creamy macaroni cheese herbs
179|no|no|no|yes|salad|2|100|100|cropped at edge|simple|angled|medium||Fig halves are topped with blue cheese and walnuts beside greens.|fig blue cheese walnut salad
180|no|no|no|yes|burger|1|100|100|cropped at edge|simple|angled|bright||Two steamed buns contain glazed pork and pickled vegetables.|glazed pork pickled vegetable bao
'''
DATA += r'''
181|no|yes|no|yes|dessert|2|70|70||simple|angled|medium||Three powdered beignets accompany an iced coffee.|powdered beignets
182|yes|no|no|yes|rice|2|100|80|cropped at edge|simple|angled|medium||Sushi rolls are topped with shredded crab avocado and seaweed.|crab avocado topped sushi
183|no|no|no|yes|other|1|80|100|cropped at edge|medium|top|medium||A seafood boil platter includes crab lobster mussels shrimp and corn.|mixed shellfish corn boil
184|no|yes|no|yes|other|1|100|100|cropped at edge|simple|angled|medium||Sashimi and fish roe cups accompany a mound of white rice.|sashimi roe white rice platter
185|no|no|no|yes|salad|2|70|60||medium|angled|dark||Chicken fruit salad contains strawberries blueberries and orange segments.|chicken berry orange salad
186|no|no|no|yes|burger|2|100|60|cropped at edge|medium|side|medium||Two turkey and cheese sandwiches have lettuce and thick tomato slices.|turkey cheese tomato sandwiches
187|no|yes|no|yes|rice|2|90|80||medium|angled|bright||A takeout box contains glazed chicken rice and green vegetables.|glazed chicken rice vegetables
188|yes|no|no|yes|salad|1|100|80|cropped at edge|simple|angled|medium||A falafel salad bowl has shredded cabbage peppers and creamy dressing.|falafel cabbage pepper salad
189|no|no|no|yes|other|3plus|50|70|main dish ambiguous|complex|angled|medium||Partly eaten tofu dishes and fried rice fill a table.|tofu fried rice meal
190|no|no|no|yes|salad|1|100|100|cropped at edge|simple|top|medium||A chicken salad includes black beans corn avocado and crisp tortilla strips.|chicken black bean corn salad
191|no|no|no|yes|burger|1|100|80|cropped at edge|simple|angled|dark||A poached egg and greens sit on dark toast.|poached egg greens dark toast
192|no|yes|no|yes|rice|1|100|100|cropped at edge|simple|angled|bright||A long sushi roll is topped with diced cucumber and creamy orange sauce.|diced cucumber orange sauce sushi
'''
DATA += r'''
193|no|yes|no|yes|other|3plus|100|70|cropped at edge|medium|angled|bright||Fried eggs hash browns and toast accompany plates of waffles and bacon.|egg hash brown toast breakfast
194|no|no|no|yes|dessert|1|100|100|cropped at edge|simple|angled|medium||A sweet bowl has watermelon jelly nuts and crushed ice.|watermelon jelly ice dessert
195|no|no|no|yes|burger|1|100|100|cropped at edge|simple|side|bright||A folded white corn cake is filled with shrimp shredded cheese and vegetables.|shrimp cheese stuffed arepa
196|no|no|no|yes|salad|2|100|90|cropped at edge|simple|angled|bright||A salad is topped with fried chicken bacon egg and grated cheese.|fried chicken bacon egg salad
197|no|no|no|yes|rice|1|100|60|cropped at edge|simple|angled|medium||Four lightly seared fish nigiri sit beside cucumber slices.|seared fish nigiri
198|no|yes|no|yes|fried|1|100|90|cropped at edge|simple|angled|medium||Fried bite sized pieces are coated in creamy orange sauce and herbs.|creamy orange fried bites
199|yes|yes|no|yes|noodle|2|100|90|cropped at edge|medium|angled|bright||Rigatoni contains spinach dark olives and sun dried tomatoes.|spinach olive tomato rigatoni
200|no|yes|no|yes|burger|2|100|100|cropped at edge|simple|side|bright||Two burgers have avocado and melted pale cheese.|avocado pale cheese burgers
201|no|yes|no|yes|salad|3plus|100|60|main dish ambiguous|complex|side|medium||A green salad sits between pizza and another pasta dish.|green salad pizza meal
202|no|no|no|yes|fried|1|100|100||simple|top|medium||Curly fries are topped with sliced jalapenos and orange sauce.|jalapeno orange sauce curly fries
203|no|no|no|yes|rice|2|60|80|cropped at edge|simple|angled|medium||Sliced chicken and cilantro top a bowl of rice beside shredded salad.|cilantro chicken rice
204|no|yes|yes|yes|fried|1|100|80||simple|angled|medium||Small fried cups contain chickpeas in a promotional food image.|chickpea fried cups
'''
DATA += r'''
205|no|yes|no|yes|grill|3plus|90|60|cropped at edge|complex|angled|medium||A grilled fish fillet sits over rice with yellow and green sauces.|grilled fish rice yellow green sauce
206|no|yes|no|yes|fried|1|100|70||simple|angled|medium||Nachos are topped with guacamole diced tomato and white cheese.|guacamole tomato cheese nachos
207|no|no|no|yes|burger|1|100|80|cropped at edge|medium|side|bright||A wheat sandwich contains avocado tomato carrot and greens.|avocado carrot tomato sandwich
208|no|no|no|yes|grill|3plus|100|100|cropped at edge|complex|top|medium||A barbecue platter carries ribs chicken sliced brisket and numerous sides.|ribs chicken brisket barbecue platter
209|yes|yes|no|yes|fried|1|100|60|cropped at edge|complex|angled|medium||Two puffy fried pastries sit on a square white plate.|puffy fried empanadas
210|yes|yes|no|yes|noodle|1|30|50||complex|side|medium||A chef lifts strands of pasta above a plate.|chef lifted pasta
211|no|yes|no|yes|grill|2|100|60|cropped at edge|simple|side|medium||Sliced steak is topped with crumbled cheese and thin fried onions.|steak blue cheese fried onions
212|no|yes|no|yes|other|3plus|50|40||complex|angled|dark||Raw beef slices are topped with greens and shaved cheese.|beef carpaccio shaved cheese
213|no|no|no|yes|pizza|1|70|50||simple|side|medium||A small tomato and cheese pizza sits on a raised serving stand.|small tomato cheese pizza
214|no|yes|no|yes|dessert|3plus|30|20|main dish ambiguous|complex|angled|medium||Bakery trays hold fruit pastries cookies and filled rolls.|bakery pastry cookie display
215|no|no|no|yes|burger|2|80|80|cropped at edge|simple|side|medium||A tall double bacon cheeseburger has lettuce and tomato.|double bacon cheeseburger
216|no|no|no|yes|dessert|1|70|80||complex|angled|bright||A warm cookie in a small skillet is topped with vanilla ice cream.|skillet cookie vanilla ice cream
'''
DATA += r'''
217|no|no|no|yes|salad|3plus|70|70||complex|angled|bright||Falafel balls sit over grains cucumber and creamy chopped vegetables.|falafel grain cucumber salad
218|no|no|no|yes|burger|3plus|50|40|main dish ambiguous|complex|top|bright||Two plates of bagel pieces sit beside coffee cups.|bagel pieces coffee
219|no|no|no|yes|burger|1|100|100|cropped at edge|simple|side|bright||An orange wrap contains quinoa avocado cucumber tomato and white cheese.|quinoa avocado vegetable wrap
220|no|no|no|yes|salad|2|100|70|cropped at edge|simple|angled|medium||Tomatoes and basil sit on thick round mozzarella slices.|caprese tomato mozzarella salad
221|no|no|no|yes|rice|1|100|100|cropped at edge|complex|angled|medium||A platter of spiced rice contains chicken and diced peppers.|spiced chicken pepper rice
222|no|yes|no|yes|burger|1|100|90|cropped at edge|simple|side|bright||A fried chicken sandwich has a row of pickle slices.|fried chicken pickle sandwich
223|no|no|no|yes|burger|1|100|100|cropped at edge|simple|angled|medium||Sliced vegetable wraps contain red peppers herbs and pale filling.|red pepper herb vegetable wraps
224|no|no|no|yes|burger|2|70|80|cropped at edge|complex|side|bright||A cheeseburger contains tomato red onion lettuce and pickles.|cheeseburger tomato red onion pickle
225|yes|yes|no|yes|fried|3plus|40|40|main dish ambiguous|complex|angled|medium||Diners hold large fried chicken meals above a crowded table.|fried chicken meals
226|no|no|no|yes|pizza|3plus|60|40|main dish ambiguous|complex|angled|medium||Pizza wings breadsticks and cinnamon rolls form a meal spread.|pizza wing breadstick meal
227|no|no|no|yes|other|3plus|100|40|cropped at edge|medium|side|medium||A bread cube on a fork is coated with melted yellow cheese.|cheese fondue bread cube
228|no|no|no|yes|other|3plus|60|50||complex|angled|bright||A bowl of green spinach curry accompanies layered rice and flatbread.|green spinach curry
'''
DATA += r'''
229|no|no|no|yes|dessert|1|100|100|cropped at edge|simple|angled|bright||Three cupcakes have half chocolate and half vanilla swirled frosting.|chocolate vanilla swirl cupcakes
230|no|yes|no|yes|rice|2|90|90||complex|angled|bright||A poke bowl includes tuna avocado seaweed and yellow pickled vegetables.|tuna avocado seaweed poke
231|no|no|no|yes|other|1|100|70|cropped at edge|simple|angled|medium||Small tofu cubes are coated in a glossy yellow brown sauce.|glossy tofu cubes
232|no|yes|no|yes|drink|3plus|40|50|main dish ambiguous|complex|side|bright||Rows of branded smoothies have purple green orange and yellow contents.|colorful branded smoothie display
233|no|yes|no|yes|salad|3plus|100|60|cropped at edge|medium|angled|medium||A long grilled kebab rests over lettuce and sliced white onion.|kebab lettuce onion salad
234|no|no|no|yes|rice|3plus|80|60|cropped at edge|complex|angled|medium||A rice bowl is topped with meat beans salsa greens and shredded cheese.|meat bean salsa rice bowl
235|no|no|no|yes|dessert|2|100|60|cropped at edge|medium|angled|medium||A stack of pancakes accompanies breaded fried chicken.|pancakes fried chicken
236|no|no|no|yes|burger|3plus|100|70|cropped at edge|complex|side|medium||A cheeseburger with tomato onion and lettuce accompanies fries.|cheeseburger tomato red onion pickle
237|no|no|no|yes|pizza|1|70|70||simple|top|bright||A round pizza has orange toppings and a spiral of white sauce.|white sauce spiral pizza
238|no|no|no|yes|dessert|3plus|100|90|cropped at edge|medium|angled|medium||Round fried doughnut bites are rolled in granulated sugar.|sugar coated doughnut bites
239|no|yes|no|yes|burger|3plus|100|70||medium|side|medium||A burger with leafy greens and roasted tomato sits beside thick fries.|greens roasted tomato burger
240|yes|no|no|yes|fried|1|40|50||simple|side|bright||A hand holds a crisp breaded chicken drumstick.|crispy chicken drumstick
'''
DATA += r'''
241|yes|no|no|yes|other|2|100|80|cropped at edge|medium|side|medium||Beef strips and potato wedges accompany a mound of white rice.|beef potato wedge rice plate
242|no|no|no|yes|soup|2|30|40|main dish ambiguous|medium|top|bright||Two small soup bowls sit on a wooden tray with crackers.|two creamy soup bowls
243|no|no|no|yes|rice|1|100|100|cropped at edge|simple|top|bright||A divided tray contains orange rice beans guacamole and chopped lettuce.|orange rice beans guacamole tray
244|no|no|no|yes|grill|1|100|100|cropped at edge|simple|angled|medium||A glazed salmon fillet accompanies rice broccoli and cauliflower.|salmon rice broccoli cauliflower
245|no|no|no|yes|dessert|1|70|90||simple|side|bright||A fruit bouquet includes chocolate dipped strawberries melon and pineapple.|chocolate dipped fruit bouquet
246|no|no|no|yes|fried|1|100|90|cropped at edge|simple|angled|medium||Tater tots have white sauce green sauce and chopped tomato onion topping.|pico green white sauce tater tots
247|no|no|no|yes|grill|2|100|90|cropped at edge|simple|angled|medium||A sliced bone in steak has coarse salt and a small green garnish.|sliced bone in steak
248|no|no|no|yes|other|1|90|80|cropped at edge|medium|angled|bright||A pale porridge is topped with blueberries pomegranate and pistachios.|blueberry pomegranate pistachio porridge
249|no|no|no|yes|fried|3plus|100|50|cropped at edge|complex|side|medium||Battered fish and chips accompany lemon ketchup and a dark iced drink.|battered fish chips
250|no|no|no|yes|burger|1|100|90|cropped at edge|simple|side|bright||A grilled chicken burger has avocado lettuce and thick mayonnaise.|grilled chicken avocado burger
251|no|no|no|yes|fried|1|80|40||simple|side|medium||Four fried chicken pieces are covered with glossy orange glaze.|orange glazed chicken nuggets
252|yes|yes|no|yes|burger|2|40|40||complex|angled|medium||A hand holds a cheeseburger with green peppers tomato and shredded lettuce.|green pepper tomato cheeseburger
'''

if __name__ == '__main__':
    from pathlib import Path
    import json
    p = Path(__file__).resolve().parents[1] / 'outputs' / '_inspection' / 'batch_1.json'
    p.write_text(json.dumps([line.split('|') for line in DATA.strip().splitlines() if line.strip()], indent=2), encoding='utf-8')
