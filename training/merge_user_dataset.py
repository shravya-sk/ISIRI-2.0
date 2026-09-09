import csv
import io
import json
import re
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "datasets" / "processed"
VOCAB_DIR = BASE_DIR / "datasets" / "vocabulary"
CLEAN_DATASET_PATH = PROCESSED_DIR / "clean_dataset.csv"
EXPANDED_DATASET_PATH = PROCESSED_DIR / "expanded_clean_dataset.csv"

# Raw text provided by user
USER_DATASET_TEXT = """ENGLISH,ENGLISH_TULU
Open youtube,Youtube open malpule
Go to YouTube,Youtube g pole
I want to use YouTube,Yenk youtube use mlpare undu
Open the YouTube app,Youtube app open malpule
Take me to YouTube,Yenan youtube g detondu pole
Start the YouTube website,Youtube website n start mlpule
Find something on YouTube,Youtube du dala nadle
Search YouTube for a programming tutorial,Youtube du programming tutorial nadle
Find a tutorial on YouTube,Youtube du tutorial nadle
Help me find a video on YouTube,Youtube du video nadle
Take me to the YouTube homepage,Youtube homepage gu pole
Start the YouTube app,Youtube start mlpule
Please open YouTube,Youtube open mlpule
Search for technology videos on YouTube,Youtube du technology videos naadle
Find the latest movie trailer,Latest movies da trailer naadle
Search YouTube for movie trailers,Youtube du movie trailers naadle
Find IPL highlights on YouTube,Youtube du IPL da highlights naadle
Search for cricket highlights on YouTube,Youtube du cricket highlights naadle
Find today's news on YouTube,Youtube du ini ta news naadle
Search YouTube for news,Youtube du news naadle
Find Tulu comedy videos,Tulu comedy videos naadle
Search for Tulu songs on YouTube,Youtube du tulu padya naadle
Open YouTube and search for lo-fi music,Youtube open maltdh lo-fi music naadle
Open Google.,Google open manpu
Launch Google.,Google open manpule
Go to Google.,Google g pole
Search Google for me.,Google search manpu yenk
Can you search the web?,Web search manpoliya yenk
Search the internet for me.,Internet search manpu yenk
Look this up online.,unden internet d thula
Find this information online.,undu information n online d naadle
Search for this on Google.,Unden google d naadle
Can you Google this for me?,unden google d nadoliya
Look it up on Google.,google d naadle
Find the answer online.,online d undetha answer naadle
Search the web for the latest information.,web d latest information naadle
I want to search something.,yenk dadana naadod
Help me search the internet.,internet d nadere help manpu
Find information about artificial intelligence.,artificial intelligence da bagge naadle
Search for information about Python.,Python da bagge naadle
Look up Python tutorials.,Python tutorial naadle
Search for Java tutorials.,java tutorial nadle
Find information about machine learning.,machine learning da bagge information naadle
Search for the latest AI news.,machine learning da baggeinformation naadle
Look up today's news.,initha news n naadle
Search for news about technology.,technology da bagge news n naadle
Find the latest technology news.,latest technology da bagge news n naadle
Search for information about ISIRI.,ISIRI da da bagge information naadle
Look up information about Tulu.,tulu basheda bagge naadle
Search for Tulu language information.,tulu basheda bagge information naadle
Find information about Karnataka.,karnataka da bagge information naadle
Search for information about Mangalore.,mangalore bagge information naadle
Look up colleges in Karnataka.,karnataka da colleges n naadle
Search for engineering colleges near me.,yenna kaithal d upuna engineering college naadle
Find information about Canara Engineering College.,canara engineering college da bagge information naadle
Search for the best Python courses.,best python courses naadle
Find online Python courses.,online d python courses naadle
Search for internships for computer science students.,computer science vidhyarthi g internship naadle
Find software engineering internships.,software engineering internship naadle
Search for frontend development internships.,frontend development internship n naadle
Look up job opportunities for freshers.,freshers g bele da opportunities  naadle
Search for the latest programming jobs.,latest  programming belen naadle
Find information about FastAPI.,fastAPI da bagge naadle
Search for React tutorials.,react tutorial naadle
Look up HTML and CSS tutorials.,HTML boka CSS da tutorials naadle
Search for JavaScript tutorials.,Javascript tutorial n naadle
Find a tutorial for Flask.,Flask da tutorial naadle
Search for information about GitHub.,Github da bagge naadle
Look up how Git works.,Git yencha work apund nd naadle
Search for Git commands.,Git da commands naadle
Find information about machine learning algorithms.,Machine learning algorithms da bagge information naadle
Search for Random Forest algorithm.,random forest da bagge naadle
Look up how neural networks work.,neural network yencha work apund nd naadle
Search for Shah Rukh Khan.,shah Rukh Khan n naadle
Find information about Shah Rukh Khan movies.,shah Rukh Khan na bagge naadle
Search for the latest Bollywood movies.,posath bollywood movies nadle
Look up today's movie releases.,ini release aina movie n naadle
Find movie timings near me.,movie da samaya naadle
Search for restaurants near me.,yenna kaithal d upuna resturants naadle
Find cafes near me.,yenna kaithal da cafe naadle
Search for hotels in Bangalore.,bangalore d ithina hotels n naadle
Look up places to visit in Mangalore.,mangalore d visit manpuna places naadle
Find tourist attractions in Karnataka.,karnatakod thupinanchina polika jaagalen naadle
Search for flights to Delhi.,Delhi'g popuna flight'en naadle
Find trains from Mangalore to Bangalore.,kudlad dhu Bengaluru'g popuna train n naadle
Search for bus timings.,Bus Timings n naadle
Look up today's train schedule.,initha schedule n thule
Find the nearest railway station.,Kaithal d ithina railway station naadle
Search for the nearest airport.,Kaithal d ithina airport naadle.
Look up the distance between Mangalore and Bangalore.,Kudla boka Bangalore da nadutha doora nadle.
Search for the best places to eat nearby.,Kaithal d unyere yedde jaaga nadle.
Find shopping malls near me.,Yenna kaithal uppuna shopping mall-len naadle.
Search for bookstores nearby.,Kaithal-d uppuna pusthakada angadilen nadle
Look up the price of a laptop.,laptop-da rate naadle.
Search for the best budget smartphones.,Kammi dudd'da yedde smartphonelen naadle.
Find reviews for this phone.,Ee phone-da review naadle.
Search for laptop reviews.,Laptop-da review naadle
Look up the latest iPhone.,Posa iPhone naadle
Search for the best laptops for students.,Kalpuna jokleg yedde laptop naadle.
Find information about Windows 11.,Windows 11-da bagge naadle.
Search for the latest Android version.,Posa Android version naadle.
Look up the latest Python version.,Posa Python version naadle.
Search for today's gold price.,Initha bangarda rate naadle.
Find the current petrol price.,Itteda petrol rate naadle.
Search for today's stock market news.,Initha stock market varthe naadle.
Look up the current dollar exchange rate.,Itteda dollar exchange rate naadle.
Search for the latest cricket news.,Posa cricket varthe naadle.
Find today's cricket match.,Initha cricket match naadle.
Search for the latest football news.,Posa football varthe naadle.
Look up the current IPL news.,Itteda IPL varthe naadle.
Find information about the Olympics.,Olympics-da vishaya naadle.
Search for today's important news.,Initha mukhyavaana varthe naadle.
What are the latest headlines?,Posa mukhya samacharalu daada?
Find today's top stories.,Initha mukhya varthelen naadle.
Search the web for the answer.,Uttarakadra online-d naadle.
Can you find this online?,Unden online-d naadaolaa?
Look for this information on the internet.,Ee vishayan internet-d naadle.
Search everywhere online for this.,Undekadra online-d matha kade naadle.
Find more information about this topic.,Ee vishayada bagge masthh mahithi naadle.
Can you look this up for me?,Unden yenkad naadoliya?
Search online and tell me what you find.,Online-d thud yenk panle.
Find the latest information about this.,Unda posa mahithi naadle.
Google this for me.,Unden yenkaad Google malple.
What is artificial intelligence?,Artificial Intelligence panda daada?
What is machine learning?,Machine Learning panda daada?
What is deep learning?,Deep Learning panda daada?
What is Python?,Python panda daada?
What is Java?,Java panda daada?
What is JavaScript?,JavaScript panda daada?
What is HTML?,HTML panda daada?
What is CSS?,CSS panda daada?
What is React?,React panda daada?
What is FastAPI?,FastAPI panda daada?
What is Flask?,Flask panda daada?
What is an API?,API panda daada?
What is a database?,Database panda daada?
What is SQL?,SQL panda daada?
What is NoSQL?,NoSQL panda daada?
What is cloud computing?,Cloud Computing panda daada?
What is the Internet of Things?,Internet of Things panda daada?
What is IoT?,IoT panda daada?
What is natural language processing?,Natural Language Processing panda daada?
What is computer vision?,Computer Vision panda daada?
Explain artificial intelligence.,Artificial Intelligence-n vivarane malple.
Explain machine learning in simple words.,Machine Learning-n sulabhavaad panle.
Explain deep learning.,Deep Learning-n vivarane malple.
Explain neural networks.,Neural Networks-n vivarane malple.
How does machine learning work?,Machine Learning yencha kelsa malpundu?
How does an AI model learn?,AI model yencha kalpundu?
What is supervised learning?,Supervised Learning panda daada?
What is unsupervised learning?,Unsupervised Learning panda daada?
What is reinforcement learning?,Reinforcement Learning panda daada?
What is classification in machine learning?,Machine Learning-d Classification panda daada?
What is regression?,Regression panda daada?
What is clustering?,Clustering panda daada?
What is a dataset?,Dataset panda daada?
What is a feature in machine learning?,Machine Learning-d Feature panda daada?
What is an algorithm?,Algorithm panda daada?
What is a programming language?,Programming language panda daada?
What is object-oriented programming?,Object-oriented programming panda daada?
What is a class in programming?,Programming-d class panda daada?
What is an object in programming?,Programming-d object panda daada?
What is inheritance?,Inheritance panda daada?
What is polymorphism?,Polymorphism panda daada?
What is encapsulation?,Encapsulation panda daada?
What is abstraction?,Abstraction panda daada?
What is a variable?,Variable panda daada?
What is a function?,Function panda daada?
What is a loop?,Loop panda daada?
What is a conditional statement?,Conditional statement panda daada?
What is a list in Python?,Python-d list panda daada?
What is a dictionary in Python?,Python-d dictionary panda daada?
What is a tuple in Python?,Python-d tuple panda daada?
What is a set in Python?,Python-d set panda daada?
What is the difference between a list and a tuple?,List boka tuple-da nadu daada vyathyasa?
What is the difference between Python and Java?,Python boka Java-da nadu daada vyathyasa?
What is the difference between HTML and CSS?,HTML boka CSS-da nadu daada vyathyasa?
What is the difference between frontend and backend?,Frontend boka backend-da nadu daada vyathyasa?
What is frontend development?,Frontend development panda daada?
What is backend development?,Backend development panda daada?
What is full stack development?,Full stack development panda daada?
What is web development?,Web development panda daada?
What is software development?,Software development panda daada?
Why is Python popular?,Python dayeg ishtond popular?
Why is machine learning useful?,Machine Learning dayeg upayogavaadundu?
Why do we need databases?,Yenkleg database dayeg bodu?
Why do websites use APIs?,Website-lu API dayeg use malpuva?
How does a website work?,Onji website yencha kelsa malpundu?
How does a browser work?,Onji browser yencha kelsa malpundu?
How does the internet work?,Internet yencha kelsa malpundu?
How does Wi-Fi work?,Wi-Fi yencha kelsa malpundu?
How does GPS work?,GPS yencha kelsa malpundu?
How does Bluetooth work?,Bluetooth yencha kelsa malpundu?
What is a computer network?,Computer network panda daada?
What is an IP address?,IP address panda daada?
What is a server?,Server panda daada?
What is a client?,Client panda daada?
What is HTTP?,HTTP panda daada?
What is HTTPS?,HTTPS panda daada?
What is a URL?,URL panda daada?
What is a domain name?,Domain name panda daada?
What is a web server?,Web server panda daada?
What is cybersecurity?,Cybersecurity panda daada?
What is encryption?,Encryption panda daada?
What is authentication?,Authentication panda daada?
What is cloud storage?,Cloud storage panda daada?
What is Git?,Git panda daada?
What is GitHub?,GitHub panda daada?
What is version control?,Version control panda daada?
What is open source software?,Open source software panda daada?
What is an operating system?,Operating system panda daada?
What is RAM?,RAM panda daada?
What is a CPU?,CPU panda daada?
What is a GPU?,GPU panda daada?
What is a hard drive?,Hard drive panda daada?
What is an SSD?,SSD panda daada?
What is the difference between RAM and storage?,RAM boka storage-da nadu daada vyathyasa?
What is a smartphone?,Smartphone panda daada?
What is a Raspberry Pi?,Raspberry Pi panda daada?
What is voice recognition?,Voice recognition panda daada?
How does speech recognition work?,Speech recognition yencha kelsa malpundu?
What is voice assistance?,Voice assistance panda daada?
How does a voice assistant work?,Voice assistant yencha kelsa malpundu?
Set an alarm.,Alarm deele.
Set an alarm for 7 AM.,Kaande 7 ganteg alarm deele.
Wake me up at 6 AM.,Yennanu kaande 6 ganteg lakyelle.
Set my alarm for tomorrow morning.,yelle kaandeg yenna alarm deele.
Create an alarm for 8 AM.,Kaande 8 ganteg alarm deele.
Can you set an alarm for me?,Yenkaad onji alarm deepara?
I need an alarm at 7:30 AM.,Yenk kaande 7:30-g alarm bodu.
Set an alarm for 9 tonight.,Inchi ratre 9 ganteg alarm deele.
Wake me up at 5:30 tomorrow.,yelle kaande 5:30-g yennanu lakyelle.
Set my morning alarm.,Yenna kaandeda alarm deele.
Create a wake-up alarm.,Lakkayere onji alarm deele.
Set an alarm for 6:30.,6:30-g alarm deele.
Remind me to wake up at 7.,7 ganteg lakkayere yenk nenpu malple.
I want to wake up at 5 AM.,Yenk kaande 5 ganteg lakkaodu.
Please set an alarm for 8 tomorrow.,Dayamalthd yelle 8 ganteg alarm deele.
Set an alarm for 10 AM.,Kaande 10 ganteg alarm deele.
Wake me at 6:15 AM.,Kaande 6:15-g yennanu lakyelle.
Create an alarm for 7:45 AM.,Kaande 7:45-g alarm deele.
Set my alarm for 5:30.,Yenna alarm 5:30-g deele.
I need to wake up at 6 tomorrow.,Yenk yelle kaande 6 ganteg lakkaodu.
Set an alarm for Monday morning.,Somavara kaandeg alarm deele.
Wake me up at 7 every morning.,prathi kaande 7 ganteg yennanu lakyelle.
Set a daily alarm for 6 AM.,prathi dina kaande 6 ganteg alarm deele.
Create a recurring alarm for 7 AM.,prathi dina 7 ganteg barpuna alarm deele.
Set my morning alarm for 6:30 every day.,Yenna kaandeda alarm prathi dina 6:30-g deele.
Wake me up at 5 AM every weekday.,Weekdays-d prathi dina kaande 5 ganteg yennanu lakyelle.
Set an alarm for every morning at 7.,prathi kaande 7 ganteg alarm deele.
I want a daily wake-up alarm at 8.,Yenk prathi dina 8 ganteg lakkere alarm bodu.
Set an alarm for weekdays at 6:30.,Weekdays-d 6:30-g alarm deele.
Create a recurring alarm at 7:30 AM.,prathi dina 7:30-g barpuna alarm deele.
Cancel my alarm.,Yenna alarm cancel malple.
Turn off my alarm.,Yenna alarm off malple.
Delete the alarm.,Alarm delete malple.
Remove my morning alarm.,Yenna kaandeda alarm deppule.
Cancel the 7 AM alarm.,Kaande 7 ganteda alarm cancel malple.
Delete my 6 AM alarm.,Yenna kaande 6 ganteda alarm delete malple.
Turn off the alarm for tomorrow.,yelledha alarm off malple.
Remove all my alarms.,Yenna maatha alarmlen deth paadle.
Cancel all alarms.,Maatha alarmlen cancel malple.
Stop my morning alarm.,Yenna kaandeda alarm untaale.
Show my alarms.,Yenna alarmlen thojale.
What alarms do I have?,Yenk vov matha alarmlu undu?
List my alarms.,Yenna alarmleda patti thojale.
Do I have an alarm set?,Yenk vovanda alarm deethundaa?
Check my alarms.,Yenna alarmlen check malple.
What time is my next alarm?,Yenna bokkada alarm yee ganteg?
When is my next alarm?,Yenna bokkada alarm yepaga?
Tell me when my alarm will ring.,Yenna alarm yepaga barpundu panle.
Show me my scheduled alarms.,Schedule aathina yenna alarmlen thojale.
Do I have a morning alarm?,Yenk kaandeda alarm undaa?
Set an alarm for 10 minutes from now.,Ittedud 10 minute-g alarm deele.
Wake me up in 20 minutes.,20 minute-d yennanu lakyelle.
Set an alarm after 30 minutes.,30 minute aayin bokka alarm deele.
Create an alarm for 1 hour from now.,Ittedud 1 ganteda bokka alarm deele.
Wake me up in an hour.,Onji ganteda ulai yennanu lakyelle.
Set an alarm for 45 minutes from now.,Ittedud 45 minute-g alarm deele.
Remind me to wake up in 15 minutes.,15 minute-d lakkayere yenk nenpu malple.
Set a timer-like alarm for 30 minutes.,30 minute-g onji timer lakada alarm deele.
Wake me up after two hours.,Radd gante aayin bokka yennanu lakyelle.
Set an alarm 90 minutes from now.,Ittedud 90 minute-g alarm deele.
Set an alarm for noon.,Madhyahnoga alarm deele.
Set an alarm for midnight.,Madhyaratreg alarm deele.
Wake me at noon tomorrow.,yelle madhyahno yennanu lakyelle.
Set an alarm for 12:30 PM.,Madhyahno 12:30-g alarm deele.
Wake me up at 4:45 PM.,Bayya 4:45-g yennanu lakyelle.
Set an alarm for 11 PM.,Ratre 11 ganteg alarm deele.
Create an alarm for 9:15 tonight.,Inchi ratre 9:15-g alarm deele.
Set an alarm for 3 PM tomorrow.,yelle madhyahno 3 ganteg alarm deele.
Wake me up at 5:45 tomorrow morning.,yelle kaande 5:45-g yennanu lakyelle.
Set an alarm for 8:20 AM.,Kaande 8:20-g alarm deele.
Change my alarm to 7 AM.,Yenna alarm-n kaande 7 ganteg badal malple.
Move my alarm to 8 AM.,Yenna alarm-n 8 ganteg move manpule
Change the 6 AM alarm to 6:30.,Kaande 6 ganteda alarm-n 6:30-g badal malple.
Edit my morning alarm.,Yenna kaandeda alarm-n edit malple.
Change tomorrow's alarm to 7:30.,yelleda alarm-n 7:30-g badal malple.
Reschedule my alarm to 9 AM.,Yenna alarm-n kaande 9 ganteg reschedule malple.
Make my alarm earlier.,Yenna alarm-n kooda bega deele.
Make my alarm later.,Yenna alarm-n kooda pira deele.
Set another alarm.,Koodonji alarm deele.
Add a second alarm for 8 AM.,Kaande 8 ganteg raddaneda alarm add malple.
Create another morning alarm.,Koodonji kaandeda alarm deele.
Set two alarms for tomorrow.,yelleg radd alarm deele.
Add an alarm for 6:30 AM.,Kaande 6:30-g onji alarm add malple.
I need another alarm at 9.,Yenk 9 ganteg koodonji alarm bodu.
Set an alarm for my class tomorrow.,yelle yenna class-gaad alarm deele.
Wake me up before college.,College-g povadud dumbe yennanu lakyelle.
Set an alarm for my exam tomorrow.,yelle yenna exam-gaad alarm deele.
Wake me up before my meeting.,Yenna meeting-d dumbe yennanu lakyelle.
Set an alarm before my flight.,Yenna flight-d dumbe alarm deele.
Remind me to wake up early tomorrow.,yelle kaande bega lakkayere yenk nenpu malple.
Make sure I wake up at 6.,Yaan 6 ganteg lakki lekka thole.
Don't let me oversleep tomorrow.,yelle yaan jaasthi jelpuna lekka thovadchi.
I need to wake up early.,Yenk bega lakkaodu.
Please wake me up tomorrow morning.,Dayamalthd yelle kaande yennanu lakyelle.
Set an alarm for tomorrow.,yelleg onji alarm deele.
I want an alarm for tonight.,Yenk inchi ratreg onji alarm bodu.
Set an alarm for later.,Bokkagaad onji alarm deele.
Schedule a wake-up alarm.,Lakkayere onji alarm schedule malple.
Can you schedule an alarm for me?,Yenk onji alarm schedule malpuvara?
Please create a new alarm.,Dayamalthd onji posa alarm deele.
Let's go to the beach tomorrow evening.,yelle bayyag beach-g poyi.
How are you? I'm so happy to see you.,Yencha ullar? Niklen thood yenk masth kushi aandu.
"I have to go, hurry up!","Yaan povodu, bega malple!"
Where will we go tomorrow? At what time will you be coming?,yelle nama olpa poyi? Eer yee gantege barpar?
Every morning I eat almonds.,yepala kaande yaan badam thinpe.
"The weather is beautiful today, so let's go outside?","Initha havamana masth laikundu, andekaad pidayi poya."
One of my friends is studying in your college.,Yenna onji dhosthi irena college-d kalthondulle.
He is currently in his final year.,ayeitte final year-d ulle.
"He is a very nice guy, nobody must disturb him.","aye masth yeddae huduge, yerla aayeg thondare malpere balli."
I am going home.,Yaan illag povond ulle.
I will go to my home.,Yaan yenna illag pope.
"Today morning I woke up at 7 and it was raining, so I went back to sleep.","Ini kaande yaan 7 gantege lakkede bokka barsa baronthithend, aik pira jethe."
"I forgot to put my phone on charge, so it switched off.","Yaan phone charge-g paadere marath pond, airdaadh av switch off aand ."
I had severe stomach pain,Yenk masth banji beene ithend.
Can you please wait for me while I get ready to go outside?,Yaan pidayi poyer ready aape aade mutta yenkaad unthuvaraa?
All set for tomorrow?,yelleg matha tayaaratha?
"You wait here, I'll go quickly and come back.","Eer moolpa unthle, yaan bega podh barpe."
I have to cook. I'll talk to you later.,"Yenk aduge malpare undu ,Yaan bokka paaterve."
How are you all?,yencha ullar maatherla?
"Why are you doing this, what is the use?","unden Dayeg  malthondullar, daada prayojana undetha?"
My grandmother's home.,Yenna abbana ill.
"Your actions, not your words, define you.","Irena bele matra irena gurtha, irena paathera ath."
Good character is a person's true wealth.,yedde guna onji naramanyana nija aayina sampath.
"What man, it's raining beautifully, let's eat hot goli bajes and chat with our friends.","Daada maare, barsa masth laaik aadh barondundu, becha becha goli baje thinded dhosthi nakuleda paaterga."
The cat is on the scooter.,Puche scooter-da mith undu.
"Due to heavy rainfall, a holiday has been declared for school children.",Jaasthi barsa barpunerdaadh school da jokleg raja korther.
"When you come near the sea, the waves give you so much joy.","Samudrada kaithal bannaga, aleyalu masthh kushi korpund."
How are you?,Yencha ullar?
Get ready for school. I have packed fish kajipu and rice for the tiffin box.,School-g tayaraale. Tiffin box-g meen da saar boka nuppu kattude.
I had to go somewhere else.,Yenk odena poyere ithend
"How are you, have you finished your lunch?","Yencha ullar, vanas aanda?"
Switch off the fan.,Fan off malple.
I am drinking water.,Yaan neer parondulle.
I am feeling dizzy.,Yenk marka avond undu.
Sit on the chair.,Kurchid kullule.
Go drink water and come.,neer pardh bale pole.
Add some sugar and salt.,Onchooru sakkare boka uppu paadle.
Ask your friends to fill out the form.,Irena dhosthi nakleg form fill malpere panle.
How much does it cost?,Undek yeth kaas?
What's the time now?,Itte gante yeth aandu?
Give me the latest technology news.,Posa technology varthe yenk korle.
Fill the bottle with hot water.,Bottle-g becha neer dinjale.
"Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday.","Somavara, Angaraka, Budhavara, Guruvara, Shukravara, Shanivara, Aithaara."
"Students, please keep quiet.","jokle, dayamalthd shanthoode uppule."
"Open the door, close the door.","Bakil deppule, bakil mucchle."
What is your name? Nice to meet you.,Irena pudar daada? Iren thood kushi aandu.
Is there someone here who teaches Kannada?,Moolpa Kannada kalpaavuna yeranda ulleraa?
"If you would like to contribute again, please fill and submit a new form.","Eer kooda sahayaka malpuna aanda, dayamalthd posa form fill maltd submit malple."
Create one new Gmail account.,Onji posa Gmail account create malple.
"Eyes, mouth, nose, cheeks, ears, neck, hands, leg, face, stomach, head, shoulder, fingers.","Kannu, baayi, mooku, kenne, kebi, barlu, kai, kaar, mone, banji, tare, bhuja, birel."
I cleaned my room before leaving.,Popunerd dumbe yaan yenna room nit malte.
I saved the document on my laptop.,Yaan laptop-d document save malte.
I met an old friend yesterday.,Kodane yaan yenna  dhosthin thikkide.
"I was getting late, so I didn't have time to have breakfast.","Yenk porthu aavondundu, aikaad kaandeda thindi thinyere porthu thikkiji."
"How are you, my friend?","Yencha ulla, yenna dhosthi?"
The breeze of our hometown is the peace of our hearts.,Namma oorda gali namma gundeda shanthi.
Close the tab and go back.,Tab mucchid pira pole.
What happened to your teeth?,Irena koolig daada aandu?
My friends are going out to roam around.,Yenna dhosthi nakul thirgare povond uller.
"Hello Isiri, can you hear me?","Namaskara Isiri, yenna paathera kenunda?"
Increase the volume by 20 percent and read it for me.,Volume-n 20 percent jaasthi manthed yenkaad odle.
water,Neer
home,Ill
house,Ill
she,Aalu
he,Aaye
him,Aayag
her,Aaleg
breakfast,Kaandeda thindi
lunch,Madhyahnoda vanaas
dinner,Ratreda vanaas
morning,Kaande
afternoon,Madhyana
evening,Bayya
them,Akleg
they,Akulu
father,Amme
mother,Appe
elder sister,Akka
younger sister,Megdi
brother,anne
elder brother,Palaye
younger brother,Megye
sister,Megdi
uncle,Maamu
aunty,Maami
Where are you,Olpa ullar
what are you doing,Daada malthondullar
wife,Bodedi
Nephew,Marumaye
husband,Kandani
year,Varsha
month,Thingolu
moon light,chandrada bolpu
time,Porthu
day,Dina
week,Vaara
date,Tariku
new moon day,Amavasye
full moon day,Punname
sunday,Aithaara
monday,Somavara
tuesday,Angaraka
wednesday,Budhavara
thursday,Guruvara
friday,Shukravara
saturday,Shanivara
sweet,cheepe
bitter,Kaipe
salty,Uppu
sour,Puli
spicy,Kara
Insipid,Sappe
Astringent,Gare
tiger,Pili
lion,Simha
bear,Karadi
dog,Naayi
fox,Kudke
goat,Aadu
bull,bori
snake,Uchhu
squirrel,chanil
turtle,Aame
mouse,Yeli
cow,Petha
monkey,Mange
pig/boar,Panji
cat,Puche scooter-da mith undu.
this is for you,Undu nikkaad
I go to school,Yaan school-g pope
you write one story every week,Ee prathi vaara onji kathe barepa
Dog barks at night daily,Naayi prathi rathre korepundu
I wash my bike every Sunday,Yaan prathi aithaara yenna bike dekkuve
cow gives milk,Petha per korpund
birds fly in the sky,Pakkilu aakashod paarpuva
i will go home tomorrow,Yaan yelle illag pope
i will meet you on sunday,Yaan nik aithaara thikkuve
everything will be fine,Matha sari aavu
i will wait for you,Yaan nik kaapuve
always,Yepala
children went to school,Joklu school-g poyer
I learnt tulu,Yaan Tulu kalthe
I closed the door,Yaan baakil mucchide
I had work yesterday,Yenk kodane kelsa ithend
I opened the door,Yaan baakil dethe
he felt bad,Aayag bejar aand
the rice is cooked,nuppu beithnd
guests,Binner
I have seen that movie three times,Yaan aa cinema-n mooji sarti thoothe
they have bought a new car,Akulu onji posa car dettonder
beautiful girl,Porluda ponnu
I saw one big house,Yaan onji malla ill thuye
He is my old friend,Aaye yenna porthuda dhosthi
There are seven rooms in my house,Yenna illad yelu room-lu undu
hundred people,Noodu jana
warm,Becha
happy life,Kushitha jeevana
You should sleep early,Ee bega jeppodu
what should i do,Yaan daada malpodu
you may go now,eer ithe povoli
may i come in,Yaan ulai baroliya
should not tell a lie,sullu panre balli
they could not speak yesterday,Akleg kode paaterere aayiji
when did you come,Eer yepa baidini
let us meet this evening,Nama ini bayyag thikega
I will come lately,Yaan porthaadh barpe
here,Moolpa
There,Alpa
down/below,Tirth
above/upon,Mith
Go there,Alpa pole
look there,Alpa thoole
you were in front of me,Eer yenna yedur ithar
move forward,yedur pole
come back,Pira bale
don't go anywhere,odegla povorchi
college,College
will you come today,Ini barpara
Where do you live,Eer olpa uppuni
I,Yaan
You,Ee
how did you come,Eer yencha bathini
god bless you,Devare yedde malpad
Don't do like that,Ancha malporchi
I will come soon,Yaan choor porthud barpe
Speak a bit louder,Onchooru gattid paatherle
Speak a bit softer,Onchooru mellane paaterle
This work should be done quickly,Ee bele bega aavodu
Suddenly it rained,Achanaka barsa bathend
I will go and come quickly,Yaan bega podh barpe
she sings very nicely,Aal masthh shok padhya panpal
I didnt do anything,Yaan daala mandiji
let us go together,Nama ottige poyi
she came to visit you,Aalu iren thooyere baidini
I was busy therefore i could not come,Yenk kelsa ithend aik  barre aayiji
why did you come,Eer dayeg bathini
Then whats special,Bokka daada vishesha
I live in Mangalore,Yaan Kudlad uppun
Do you speak Tulu,Eer Tulu pathervara
I can speak Tulu,Yenk Tulu paatherere barpundu
I do not speak Tulu,Yenk Tulu paatherere barpuji
I am learning Tulu,Yaan Tulu kalthondulle
Nice to meet you,Iren thood kushi aand
Thank you very much,masthh solmelu
Thank you,Solmelu
very,masthh solmelu
unique,Vishesha
different,Vithyasa
like,ishta
continue,Mundarisale
to,-g
words,shabdolu
details,Vivarane
name,Pudar
milk,Per
no,Ath
come,Bale
don't come,Barorchi
call,Leppule
nature,Prakrithi
environment,Parisara
write,Barele
read,Odle
on,On
off,Off
light,Bolpu
tv,TV
leg,Kaar
umbrella,Kode
rice,Nuppu
explain,Vivarane malple
tell,Panle
more,Jaasthi
open,thereyunu
turn on the fan,Fan on malple
turn off the fan,Fan off malple
on the lights,Bolpu on malple
off the lights,Bolpu off malple
door,Baakil
speak,Paatherle
talk,Paatherle
photo,Photo
video,Video
change,Badalavane
mental,Manasika
small,Yellya
share,Pattunu
flower,Poo
animal,Mruga
animals,Mrugalu
bird,Pakshi
yes,Andh
search,nadle
bottle,Bottle
elders,hiriyer
younger,yelya
eldest,mallal
cover,Muchunu
help,Sahaya
What is your name,Irena pudar daada
What is this,Undu daada
Had tea,Cha aanda
It should be like that only,av Anchene uppod
I will never let you win easily,Yaan ninan ath sulabhod gendhere  budpuji
He was in trouble,Aaye thondared ithe
want,Bodu
wanted,Bodaathithnd
question,Prashne
man,anjov
women,Ponjov
Long time no see,masthh porthu aandu thoovande
I can understand,Yenk artha apundu
see,Thoole
understand,Artha manthonunu
my,Yenna
handsome,Porlu
respect,Gaurava
culture,Samskrithi
temple,Devasthana
please say that again,Dayamalthed koodonji sarti panle
I love you,Yaan ninan moke malpuve
Get well soon,Bega ushaar aale
fast,Bega
I want to get down here,Yenk moolpa jappodu
study,Kalpu
studying,Kalthondulle
language,Bhashe
bad,Pade
good,yedde
bad words,Pade paathera
boy,Aan
girl,Ponnu
responsibility,Javabdari
busy,Busy
go,Pole
escape,Parari
next,Bakkada
best,masth yedde
surprise,Aascharya
sun,Soorye
moon,Thingolu
sky,Aakasha
fight,Ladaayi
compromise,Rajinama
war,Yuddha
earth,Bhoomi
cloth,Kuntu
clothes,Kuntulu
shirt,shirt
pant,Pant
saree,Seere
army,Sainika
aeroplane,Vimana
skin,charma
information,Mahithi
movie,Cinema
welcome,Swagatha
straight,sartha
left,Yedath
forward,Dumbu
about,Bagge
back,Pira
outside,Pidayi
Inside,Ulai
smile,Thelike
angry,Kopa
emotion,Bhavane
Thirsty,bajhel
hungry,badav
right,Balath
Sit down,Kulle
No problem,Thondare ijji
not good,yedde ath
plant,Dayi
road,Raste
bye,Podh barpe
Okay,Aavoli
Enough,Yedde
learning,Kalpun
enemy,Shatru
teaching,Kalpaavun
friend,Dhosthi
tree,Mara
book,Pusthaka
eat,Tinle
sleep,Jelple
jump,lagile
everyone,Matherla
anyone,Yerandala
model,Model
library,Granthalaya
lesson,Paata
guest,Binner
partner,Paaludari
marriage,Madime
god,Dever
beach,Beach
dictionary,Shabdakosha
collect,Koodsle
none,Yerla ijji
text,Baraha
person,Naramanye
sad,Bejar
depressed,Manasika bejar
target,Lakshya
daily,Prathi dina
everyday,Prathi dina
and,boka
of,-da
the,Undu
for,-gaad
is,Undu
that,Avu
by,-dud
this,Undu
with,Ottuge
it,Avu
not,Ath
or,Athanda
be,Upple
are,Ullar
from,-dud
at,-d
as,Lekka
your,Irena
all,Matha
have,Undu
new,Posa
was,Ithend
we,Nama
will,-ve
can,Aapu
us,Yenkleg
if,Aanda
page,Puta
has,Undu
free,Puchhada
but,Aanda
our,Namma
other,Bere
do,Malple
site,Jaaga
today,Ini
tomorrow,yelle
up,Mithaari
may,Aavoli
yesterday,Kode
now,Ithe
what,Daada
after,Bokka
together,Ottige
which,Voo
their,Aklenna
news,Varthe
use,Upayoga
any,Vovandaala
only,Matra
so,Aikaadh
his,Aayana
when,Yepa
contact,Samparka
rain,Barsa
go inside,Ulai pole
go outside,Pidayi pole
walk slowly,Mellaane nadapule
business,Vyapara
i forget,Yenk marathend
who,Yer
go far,Doora pole
also,Kooda
get,Padedole
don't touch,mutthorchi
view,Thoole
first,Suru
am,yan
been,Aathnd
would,Aapundu
how,Yencha
heat,Becha
were,Ither
some,Kelaavu
click,Othu
service,Seve
find,Naadla
price,Kraya
list,Patti
just,Mathra
over,mugind
state,Rajya
stand,Unthule
into,Ulai
stare,masepuni
one,Onji
two,Radd
three,Mooji
four,Naal
five,Ayn
six,Aaji
seven,Yelu
eight,Yenma
nine,Yormba
ten,Patt
eleven,Patinonji
twelve,Padradd
thirteen,Padmooji
fourteen,Padnaal
fifteen,Padinayn
sixteen,Padinaaji
seventeen,Padinyelu
eighteen,Padinpenma
nineteen,Padnormba
twenty,Irva
hundred,Noodu
health,Arogya
world,Loka
used,Galasina
work,bele
most,masthh
last,Kadetha
music,Sangeetha
dance,Nrutya
system,Vyavasthe
number,Sankhye
please,Dayamalthd
available,Thikkuna
support,Sahaya
message,Sandesha
well,Ushaar
rights,Hakkulu
through,Moolaka
order,Aadesha
equal,Samana
life,Jeevana
tension,Tension
activity,Kelsa karyagalu
history,Ithihasa
past,Kaledina
present,Itteda
future,mundaag
focus,Gamana
analyse,Parikshe malple
evidence,Sakshi
main,Mukhya
truth,Nija
assist,Sahaya malple
concentrate,Gamana
method,Vidhana
abundance,Samruddhi
Illusion,Maaye
Adventure,Saahasa
country,Desha
sincere,Nijavaayina
disturb,upadhra
sense,Artha
teach,Kalpavunu
practice,Abhyasa
justice,Nyaya
reason,Kaarana
test,Parikshe
train,Kalpale
mature,parva
preserve,oripavuni
separate,vangada
masther,yajamaane
shame,Naachige
scold,nerpun
queue,saalu
noise,Shabda
decide,Theermana malpule
trouble,Thondare
family,Kutumba
born,Puttuni
hospital,Aaspathre
silly,Yellya
arrange,vyavasthe manpule
control,Niyanthrana
format,vinyasa
snore,guruke
scent,Vaasane
peep,nilkuni
sip,parpuni
scamper,Parari
hiccup,ekkade
fan,Fan
dont,Balli
never,Yepala ijji
let,Budle
win,Gendunu
lose,Soopuni
easily,Sulabod
down,Tirth
sit,Kullyer
sentence,Vakya
honesty,Satya
dishonesty,sullu
machine,Machine
detail,Vivarane
student,Kalpunaye
children,Joklu
enter,Ulai bale
entry,Pravesha
exit,Pidayi pole
tulu,Tulu
english,English
kannada,Kannada
tamil,Tamil
telugu,Telugu
trust,Nambike
cloud,Moda
glow,Bolpu
globe,Bhoomi
charge,Charge
planet,Graha
lecture,Paata
teacher,Mestru
baby,Yellya baale
client,Grahake
discover,Naaduni
hands,Kaikulu
legs,Kaarulu
eyes,Kannulu
lips,dudi
waist,Sonta
wrist,Manikattu
laugh,Telipini
shower,Meepuni
laughing,Telipuna
report,Varadi
ask,Ken
task,bele
mask,Mask
mass,Gumpu
computer,Computer
old,parath
run,Balip
walk,Nadap
seashore,Kadal kare
tongue,Naalai
ears,Kebikulu
nose,Mooku
mouth,Baayi
opportunity,Avakasha
score,Anka
twist,piripuni
squiz,squiz
sneeze,Thumbil
snuff,snuff
shuffle,Bereke
research,Samsodhane
investigate,Toodu
struggle,Kasta
obstacle,Adathada
impression,Prabhava
expression,Bhavane
impress,Khushi malple
express,Panle
bus,Bus
cheat,Mosa malple
thief,Kalve
anxious,Aatanka
blabber,Galarane
ticket,Ticket
word,Uttara
compensate,Parihara
cross,Daatun
going,Povonduller
gone,Pothund
went,Poyer
school,Shale
singer,Padhya panpunar
dancer,Narthaka
anklet,Gejje
ankle,Gant
instrument,Upakarana
where,Olpa
whom,Yereg
whose,Yerna
why,Dayeg
drink,Parle
jackfruit,Pelakkai
watermelon,bachankai
apple,Apple
mango,Kukku
pot,madike
hot,becha
spoon,Spoon
ladle,Kailu
driver,Driver
ride,Savari
horse,Kudure
king,Raje
queen,Rani
plan,yojane
kill,Kerpun
conflict,Ladaayi
hill,Gudde
point,Guri
game,Gobbu
loose,sopun
finger,Beralu
ring,ungila
lost,kaled pothund
chase,beri pattuni
cut,kadpu
story,Kathe
strong,Gatti
weak,baladanthina
brave,Dhairya
clever,Ushaar
coward,pukkel
happy,Kushi
sorry,Bejaar
love,Preethi
secret,Guttu
play,Gobbele
stay,Uppule
limit,mithi
bangle,kaaji
guilty,Thappu
pity,Karuna
introduce,Parichaya malple
daughter,Magal
son,Mage
society,Samaja
evil,pagemani
death,Saavu
chilly,munchi
hard,Gatti
pickle,Uppad
prepare,Thayar
exam,Parikshe
simply,pokkade
It's not working,Undu bele manthond ijji
It’s too expensive,Undu masthh expensive
Take care,jagrathe manpule
Let’s go by bike,Nama bike-d poyi
I'm proud of you,Yenk nina mith hemmeyundu
I'm going to the market,Yaan market-g pondulle
Let’s study together,Nama ottuge kalpuga
I forgot my notebook,Yaan yenna notebook marthde
The food is ready,Vanaas tayar aand
It’s time to eat,Thinyere porthu aand
Turn off the lights,light off malple
Lock the door,Baagil lock paadle
I'm doing my homework,Yaan yenna homework malthond ulle
Let’s clean the room,room clean malpuga
It's raining outside,Pidayi barsa barondundu
Nothing much,Daadala ijji
What’s going on,Daada aavondundu
I don’t know,Yenk gottuji
I'm not sure,Yenk sarit gothuji
I agree with you,Yaan ninana oppuve
I want to buy this,Yenk unden dethonodu
I'm hungry,Yenk badavu avondundu
What’s for lunch,Madhyanag daada vanaas
The food is tasty,Vanaas masth laikundu
I don't like it,Yenk undu ishta ijji
I'm full,Yenna banji dinjind
Can I have some water,Yenk onchooru neer thikkoliya
I am happy today,Ini yenk kushi aathnd
I am tired,Yenk bejar aathnd
I am feeling sick,Yenk ushaar ijji
I am very excited,Yenk masthh kushi aathend
Its boring,Undu bore aavundu
Thats funny,Avu makkar ithend
I am scared,Yenk podige avond undu
Where are you going,Eer olpa povondullar
I am going to the market,Yaan market-g povondulle
Lets go for a walk,Nama nadapere poyi
I missed the bus,Yaan bus miss malthe
The train is late,Train porthu aathend
I love this weather,Yenk ee havamana masthh ishta
I want to travel,Yenk oor thirgodu
I will be back soon,Yaan bega pira barpe
What happened,Daada aand
Is everything okay,Matha sari undathe
I am getting ready,Yaan tayar aavondu ulle
I am going to bed,Yaan jeppere popun
Wake up early,Bega lakle
Dont be late,Porthu malporchi
Wait for me,Yenkaad unthle
Lets go home,Nama illag poyi
See you tomorrow,yelle thikga
Come here,Moolpa bale
Be quiet,manipande uppule
Dont worry,Bejar malporchi
Iam coming,Yaan barondulle
Just a minute,Onji nimisha
I am listening,Yaan kenondulle
Can I sit here,Yaan moolpa kulloliya
Its getting dark,Kattale aavondundu
Lets eat outside,Nama pidayi thinka
I dont understand,Yenk artha aaiji
Speak slowly,Mella patherle
I cant hear you,Irena pathera yenk kenond ijji
What time is it,Itte gante yeth
Give me that,Unden yenk korle
Come fast,Bega bale
Don't shout,Bobbe padorchi
Be careful,Ushaard uppule
That’s mine,Avu yenna
This is yours,Undu irena
I will do it,Yaan malpe
Let me try,Yaan prayathna malpe
Try again,Koodonji sarti prayathna malple
One more time,Koodonji sarti
Do you remember,Nikk nenepundaa
I forgot,Yaan marathede
You're right,Eer pandina sari
That’s wrong,Avu thappu
Turn off the TV,TV off malple
Don't touch that,Unden mutorchi
Clean the table,Table clean malple
It’s very hot,masth becha undu
It’s very cold,masth chali undu
I'm feeling sleepy,Yenk nidre barondundu
Let’s take a break,Onchooru break dethonga
I'll call you later,Yaan bokka call malpe
Don’t lie,sullu panorchi
Let's go to mangalore,Nama Kudlag poyi
I know mangalore well,Yenk Kudla yedde gurtha undu
What’s your name,Irena pudar daada
I’m from India,Yaan Bharathadaye
Can you help me,Yenk onji sahaya malpara
Please close the door,Dayamalthd baagil mucchle
Can you come with me,Yenna ottuge barpara
Stand up,Lakked unthule
What’s the homework,Homework daada
The teacher is coming,Mestru barondunduller
I'm late for class,Class-g porthu aand
I need help with this topic,Undu vishayad yenk sahaya bodu
I got full marks,Yenk full anka thikkend
The class was interesting,Class masth yedde ithend
"Hello, How are you","Namaskara, yencha ullar"
Had your lunch,Vanas aanda
Where are you working,Eer olpa bele malpunu
All are welcome,Maatheregla swagatha
How were the rains this year,Ee varsha barsa yencha ithend
I am fine,Yaan ushaar ulle
Will this bus go to Udupi,Ee bus Udupig popundaa
Where is this address located,Ee vilasa olpa undu
"Ok, see you next time","Aand, barpi sarthi thikega"
I will come,Yaan barpe
It was a lot of help,masth sahaya aand
How it happened,Avu yencha aand
I am happy to see you,Iren thood kushi aand
Then what is the special,Bokka daada vishesha
Then,Bokka
special,Vishesha
Nothing else,Bethe daadala ijji
Please wait for a moment,Onji nimisha untle
We will go to Mangalore,Nama Kudlag poyi
In a restaurant,Onji hotel-d
Will that take some time,Avu onchooru porthu dettonuvaa
Give me one masala dosa,Yenk onji masala dosa korle
I don't want that,Yenk avu bodchi
Give some water,Onchooru neer korle
You have given a good service,Eer edde seve korthar
The price is too high,Kraya masth jaasthi undu
Show me the new designs,Posa design-len thojale
I will pay by cash,Yaan cash kord solve
Please pack all the goods,Dayamalthd matha saamanu pack malple
What is the time now,Itte gante yeth
Good work,EDDae kelsa
What did you have for tiffin today,Ini kaande thindi daada thindar
Anything else,Bere daadandaala
How was the coffee,Coffee yencha ithnd
Coffee was good,Coffee edde ithnd
Where did you go on weekend,Weekend-g olpa poithar
This time i had gone to Bangalore,Ee sarti yaan Bangalore-g poithe
How was your weekend,Weekend yencha ithnd
It was super,masth super ithnd
I came yesterday,Yaan kodane batthe
Can you wait for me,Yenkaad untuvara
Okay i will wait,Aand yaan kaapuver
Can we meet today,Nama ini thikkoliya
stop,Untle
scratch,Geesule
give,Korle
Take,Dettonle
get up,Lakle
watch,Thoole
look,Thoole
wait,Untle
above,Mitt
important,Mukhya
verb,Kriyapada
might,Aavoli
perceived,Gothavuna
disrespect,Agaurava
talking,Paateruna
realize,Gothapuni
place,Jaaga
better,Edde
You run in the marathon,Ee marathon-d bala
You sit in this chair,Eer ee kurchid kulyer
Is it so,Anchana
Can you come there,Alpa baroliya
Didn't you know,Nikka gothijja
Glad to meet you,Iren thikkid kushi aandu
What to do now,Itte daada malpuni
See you next time,Bakkada sarti thikkoyi
Let us have a tea,Nama chaa paroyi
Can you bring a cup of water,Onji cup neer konapuvara
I will also come with you,Yaanla irena ottuge barpe
Whom should I ask,Yaan yeren kenodu
Which is your favourite color,Irena ishtada banna vovvu
You should definitely come to our house during the festival,Parbadaga eer yenna illag kanditha barodu
I have to wake up early in the morning tomorrow,Yenk kale kaande bega lakkaodu
I have some other work today,Yenk ini bere kelsa undu
Where are you man,Olpa ulla maare
I am waiting for you near Town hall,Yaan ninna kaad Town Hall kittal kaapondulle
Ice-cream at Ideal's is too good,Ideal-da Ice-cream masth laakundu
Today's treat is mine,Initha treat yenna
I will meet you in the evening,Yaan irenn bayyag thikkpe
Thank you all,Maatheregla solmelu
How much does this cost,Undek yeth kraji
What do you need,Ireg daada bodi
Which day is it today,Ini vaa dina
Day after tomorrow,Manadanyi
He knows Tulu,Aayag Tulu barpundu
She knows Tulu,Aaleg Tulu barpundu
He is a good man,Aaye edde naramanye
Are you married,Madime aathundaa
Come in be seated,Ulai bale kulyer
Where is the bathroom,Bathroom olpa undu
Excuse Me,Onchooru aache pole
He was at home,Aaye illad ithye
You ate a mango,Ee kukku thinda
We build a new house,Nama posa ill kattuda
The sun has set,Soorye kanthe
He became a Doctor,Aaye Doctor aaye
He cant walk,Aayag nadeyere aavuji
If he comes tell me,Aaye batthenda yenk panle
If it rains I will get wet,Barsa batthenda yaan nanepe
If anyone comes call me,Yerandaala betthernda yenk lekkale
Was she reading,Aalu odondithalaa
Wasnt he playing,Aaye gobbandijjaa
Werent they coming,Akulu barondijjeraa
Were you waiting for me,Eer yenkaad kaaponditharaa
They were not speaking with me,Akulu yenna kooda paaterondijjer
If you told me I would go,Eer panthitharnda yaan povonthithe
If you were here it would be nice,Eer moolpa itharnda masth edde aavontithnd
I wish you had told me,Eer yenk panthitharnda aavontithnd
Call the police,Police-g lekkale
Please speak slowly,Dayamalthd mellane paaterle
I love learning new things,Posa vishaya kalpunu yenk masth ishta
I wake up at 7am,Yaan kaande 7 gantege lakpe
I work out four days a week,Yaan vaarad naal dina gym-g pope
I go to college every day,Yaan prati dina college-g pope
Its hot out today,Ini pidayi masth bisi undu
Im sick and tired of this weather,Ee havamanadud yenk bejaraathnd
I don’t think so,Yenk ancha thojuji
Can I get you something to eat,Thinyere daadandaala konatoliya
This is my bag,Undu yenna bag
Sure no problem,"Kanditha, thondare ijji"
Its too big,Undu masth malla undu
Its too small,Undu masth yellya undu
Ill think about it,Yaan unda bagge yochane malpe
Thats expensive,Avu masth kraji
Thats cheap,Avu kammi kraji
Please give me a receipt,Dayamalthd yenk onji receipt korle
Can I exchange this,Unden badal malpoliya
Is it fresh,Undu posatha
Ill take two of these,Yaan rindund dettonpe
Please wrap it,Dayamalthd pack malple
What brand is this,Undu vaa brand
This is for a friend,Undu yenna dhosthigaad
Can I try a sample,Yaan sample thooli yaa
Keep the change,Chilli dudd deele
That was perfect,Avu masth edde ithnd
We need more time,Yenkleg kooda porthu bodi
Can I have a straw,Yenk onji straw thikkoliya
Thank you for the service,Seveg masth solmelu
No smoking please,Dayamalthd beedi parpadchi
Can we sit outside,Nama pidayi kulyoliya
We will come back later,Nama bokka pira baroyi
Where is the bus stop,Bus stand olpa undu
Where is the train station,Railway station olpa undu
Where can I buy tickets,Ticket olpa dettonoli
Turn left,Yedat thirgle
Turn right,Balath thirgle
Go Straight,Nera pole
Stop at the corner,Mooled untle
pay attention,Gamana korle
read loud,Gattid odle
time is up,Porthu mugyind
Its break time now,Itte break porthu
Thats intresting,Avu ascharya aathnd
I agree,Yaan othpe
I disagree,Yaan oppuji
Turn on the computer,Computer on malple
Turn off the laptop,Laptop off malple
Open the file,File rathle
Close the file,File mucchle
Save the document,Document save malple
Send me the mail,Yenk mail kadpule
what is your password,Irena password daada
Turn up the volume,Volume jaasthi malple
Turn down the volume,Volume kammi malple
click here,Moolpa click malple
call an ambulance,Ambulance-g call malple
I need help,Yenk sahaya bodi
Stay calm,Shanthoode uppule
Dont move,Aaladchi
i feel sick,Yenk ushaar ijji
this is urgent,Undu banga aayina kelsa
wait here,Moolpa untle
follow me,Yenna pira bale
listen to me,Yenna paatera keni
pick it up,Unden dettonle
take this,Unden dettonle
put it here,Unden moolpa deele
Show me,Yenk thojale
Welcome home,Illag swagatha
Time for dinner,Vanaasda porthu
Take some rest,Onchooru visranthi dettonle
Go to bed,Jelpere pole
Wake up,Lakle
Sweet dreams,Kushi aayina kanasu
Do your homework,Homework malple
Set the table,Table tayar malple
Take a bath,Meeyere pole
change your clothes,Kanta badal malple
clean your room,Room nit malple
sweep the floor,Nela adple
wash your hands,Kai dekkle
Just a moment,Onji nimisha
One second,Onji second
Are you serious,Nijavaadlaa
Lets see,Thooyi
Take it easy,Chill aath uppule
Lets meet again,Nama kooda thikkoyi
call me later,Bokka yenk call malpe
Life is good,Jeevana masth laakundu
how is your work,Kelsa yencha nadapundu
Its going well,Edde nadapundu
where you have been,Eer olpa ithar
I was on vacation,Yaan suteed ithye
how is your family,Irena illadayilu yencha ullar
they are fine,Akulu ushaard ullar
I am watching TV,Yaan TV thoovondulle
I am cooking,Yaan aduge malpondulle
I am reading book,Yaan pusthaka odondulle
I am cleaning,Yaan nit malpondulle
I am listening to music,Yaan paata kenondulle
I am talking to friend,Yaan dhosthido paaterondulle
I am shopping online,Yaan online shopping malpondulle
I am going out,Yaan pidayi ponduLle
I am going to the store,Yaan angadig ponduLle
I just got here,Yaan itte baide
I am here,Yaan moolpa ulle
I  will be there at 5 minutes,Yaan ayn minute-d aade barpe
Message me when you are free,Free aavaga message malple
Are you free now,Itte free ullara
I am busy right now,Itte yaan busy ulle
Lets go out for dinner,Madhyahnoda vanaasag pidayi poyi
Lets cancel it,Unden cancel malpoyi
Lets do this tomorrow,Unden kale malpoyi
Lets reschedule it,Unden reschedule malpoyi
I am allergic to dust,Yenk dhoolda allergy undu
I am on diet,Yaan diet-d ulle
Dont skip meals,Vanaas budpadchi
I am feeling better,Yenk itte ushaar anipundu
I need fresh air,Yenk posa gali bodi
Dont work too much,Jaasthi kelsa malpadchi
Relax a little,Onchooru aaraam malple
I feel lazy,Yenk soombu barondndu
Lets share ideas,Idea-len share malpoyi
I need more time,Yenk kooda porthu bodi
I am almost done,Yenna kelsa aavontu batthnd
Turn on bluetooth,Bluetooth on malple
Turn off bluetooth,Bluetooth off malple
Thats bad,Avu haal
I learned something new,Yaan posath kalthe
Lets work together,Nama ottuge kelsa malpoyi
Please expplain again,Dayamalthd koodonji sarti vivarane malple
please repeat that,Dayamalthd koodonji sarti panle
I am late for class,Class-g porthu aandu
I am preparing for test,Yaan test-g tayaraavonduLle
I need to exercise,Yaan exercise malpaodu
I am proud of you,Yenk nina mitt hemmeyundu
May be you are right,Eer pandini sari aavoli
This is dangerous,Undu apakada
someone is hurt,Yergo ghaaya aathnd
I like it,Yenk undu ishta
I am confident,Yenk nambikeyundu
I am proud of myself,Yenna mitt yenk hemmeyundu
I am in love,Yaan preethid ulle
I am sad toady,Ini yenk bejaraathnd
I will take this,Yaan unden dettonpe
Tell us your thoughts on this,Unda bagge irena abhipraya panle
Dont let it break,Undu puriyadchi
Your mind will be happy,Irena manasg kushi thikknd
India has lost both games so far,Bharatha radd matchla soothnd
She is very brave,Aalu masth dhairya
We will investigate and take action,Nama thoodu kelsa malpoyi
Girl dies of suspected dengue,Dengue barad ponnu theerind
Play with children,Jokledottu gobbele
They should do good work,Akulu edde kelsa malpaodu
Do your own chores at home,Irena illada kelsan ere malple
You have to believe that,Eer unden nambodu
They said they would fight,Akulu ladaayi malpuva pandud panther
He is also a director and singer,Aaye director mari gayake kooda
We are ready for everything,Nama maathekkla tayar ullayi
They are using them,Akulu ayen upayogisuver
Who will be the next chief minister,Bakkada mukhyamantri yer aaper
I am missing them,Yenk aklen nenpaapundu
But all of that is not real,Aanda avu matha satya att
"This time too, the same is expected",Ee sarti kooda anchene aavoli
It is not your money,Undu irena dudd att
Why have you done this,Eer dayeg incha malthar
They have no papers,Aklenada kagaji ijji
Make your payment on time,Porthugaad dudd korthle
They never expected the Indian team to win,Bharatha team gelpu pandud akulu yochane malpijer
No one is paying attention,Yerla gamana korpondijjer
Interested people can join us,Ishta ullinakulu yenkledo seroli
Looks terrifying,Thooyere tharike aavundu
But thats exactly what it is,Aanda nijavaadla avve avu
The doctors are saying she is recovering,Aalu ushaar aaponduLla pandud doctor panper
Good times coming up,Edde porthu barpundu
All services are for free,Maatha sevela free
His wife is at home,Aayana boddi illad ulla
Theres no other way,Bere saadi ijji
Everyone was smiling,Maatherla theliyonthither
Anyone can participate in this event,Yerandaala ee karyakramod bhaagavahisoli
It wasnt so simple,Avu ashtonji sulabha ithiji
Take me with you,Yennanu irena ottuge konole
The battery goes down,Battery kammi aavundu
The hall was full,Hall dinjidithnd
No one came to help us,Yenkleg sahaya malpere yerla baijer
Then it started to grow,Bokka avu buleyere suru aandu
They didnt believe it,Akulu unden nambijer
The feeling is different,Bhavane vithyasa undu
This is an endless process,Undu mugiyandina kelsa
I am the same that I was,Yaan dumbe yencha ithye anche ulle
Dont sit for too long,Jaasthi porthu kulyadchi
That is not real happiness,Avu nija aayina kushi att
Thats not the problem,Avu samasye att
Do not talk on the phone while driving,Gaadi chalpaavaga phoned paateradchi
Have you lost your Aadhaar card,Irena Aadhaar card kalad poithndaa
But no one was hiring,Aanda yerla kelsag dettonderiji
I was also interested in dance and acting,Yenkla nrutya mari acting-d ishta ithnd
Id recommend this to everyone,Yaan unden maatheregla panpe
Change is needed,Badalavane bodi
They dont have space,Akleg jaaga ijji
Who won finally in this battle,Ee ladaayid aakherig yer gelther
Action will be taken soon,Bega kelsa aavu
Congratulations to everyone involved,Bhagavahisina maatheregla abhinandane
"Eat plenty of fresh vegetables, fruits, and whole grains","Jaasthi tharukaari, phalavastu tinle"
He fainted when he saw her,Aalenn thooth aayag garane batthnd
He was appointed by the President,Aayan Rashtrapathilu nemaka malther
I have never played such a character,Yaan yapala incha pathra malpiji
They have become good friends,Akulu edde dhosthilaather
It is Indias first space film,Undu Bharathada suratha space film
He started shouting,Aaye bobbe paadere suru malte
We will find out in this article,Nama ee lekhana-d naadud padoyi
Theres no doubt in that,Ayk daada anumanala ijji
Try it you will ll like it,Prayathna malple ireg ishta aavu
This would help reduce costs,Undu kraya kammi malpere sahaya aavu
Their children are with them,Aklenna joklu aklenottugu uller
What can we expect from them,Aklenud nama daada yochane malpoli
I feel tired,Yenk bejaraathnd
She looks upset,Aalu bejard thojuvaalu
He runs fast,Aaye bega balipuve
They are waiting,Akulu kaaponduller
We must leave,Nama povaodu
You drive slowly,Eer mellane gaadi chalpaavle
I will call,Yaan call malpe
She is singing,Aalu padpaalu
He likes tea,Aayag chaa ishta
They play outside,Akulu pidayi gobbuver
We are ready,Nama tayar ullayi
You look happy,Eer kushid thojuvor
I forgot that,Yaan ayen marthde
She is cooking,Aalu aduge malponduLla
He is reading,Aaye odondulle
They are dancing,Akulu nartana malpuver
We should try,Nama prayathna malpaodu
You did well,Eer edde kelsan malthar
I will write,Yaan barepe
She looks tired,Aalu susthd thojuvaalu
He feels cold,Aayag chali aavundu
They need help,Akleg sahaya bodi
We must go,Nama povaodu
You were late,Ireg porthu aathithnd
I trust you,Yaan nina mitt nambike depe
She is smiling,Aalu theliyonduLla
He walks slowly,Aaye mellane nadapuve
They are studying,Akulu kalponduller
We should wait,Nama kaapodu
You look worried,Eer aatankad thojuvor
I am learning,Yaan kalpondulle
She likes music,Aaleg sangeetha ishta
He is laughing,Aaye theliyonduLle
They are shouting,Akulu bobbe paadonduLLer
We are coming,Nama baronduLLayi
You did nothing,Eer daadala malpiji
I was busy,Yaan busy ithye
She is strong,Aalu gatti
He is clever,Aaye ushaar
They are ready,Akulu tayar uller
We must decide,Nama theermana malpaodu
You stay here,Eer moolpa unthule
I feel sleepy,Yenk jelpu barondndu
She looks weak,Aalu nirlakshya thojuvaalu
He is hungry,Aayag banji gumpu
They look confused,Akulu gondalad thojuvor
We will try,Nama prayathna malpe
You know this,Ireg undu gothundu
I will sleep,Yaan jelpe
She is calm,Aalu shanthavaad ulla
He feels better,Aayag itte ushaar undu
They need water,Akleg neer bodi
We are late,Nama porthu aathaari
You stay quiet,Eer shanthoode unthule
I can drive,Yenk drive malpere barpundu
She sings well,Aalu edde padpaalu
He is tall,Aaye thegge
They look fine,Akulu edde thojuvor
We are done,Yenkleda aandu
You tell me,Eer yenk panle
I am ready,Yaan tayar ulle
She is angry,Aaleg kopa batthnd
He is kind,Aaye dayanvithe
They play well,Akulu edde gobbver
We must hurry,Nama bega malpaodu
You are safe,Eer surakshitha uller
I saw him,Yaan aayan thooye
She knows me,Aaleg yenna guruthe undu
He is busy,Aaye busy ulle
They look happy,Akulu kushid thojuvor
We are strong,Nama gatti ullayi
You believe me,Eer yenna mitt nambike depar
I lost it,Yaan ayen kalade
She is nice,Aalu edde
He runs daily,Aaye prati dina balipuve
We are waiting,Nama kaapondullayi
You look tired,Eer susthd thojuvor
I feel cold,Yenk chali aathnd
She is ready,Aalu tayar ulla
He looks angry,Aaye kopad thojuve
They work hard,Akulu kasta kelsa malpuver
We are safe,Nama surakshitha ullayi
You are kind,Eer dayanvithe
She reads fast,Aalu bega odpaalu
He is sick,Aayag ushaar ijji
They are late,Akleg porthu aandu
We should stop,Nama unthodu
You help me,Eer yenk sahaya malpuvar
I will join,Yaan kooda barpe
She is weak,Aalu banga
He looks smart,Aaye chalaki thojuve
They are near,Akulu kaikittal uller
We are lost,Nama saadi kaladi
You look fine,Eer edde thojuvor
I feel hungry,Yenk banji gumpu
She is brave,Aalu dhairyavantha
He is honest,Aaye satyavantha
They seem busy,Akulu busy lekka thojuvor
We should talk,Nama paaterodu
You are wrong,Eer thappu
I found it,Yenk thikknd
She is silent,Aalu shanthavaad ulla
He looks tired,Aaye susthd thojuve
They are moving,Akulu saronduLLer
We are sorry,Yenkleg bejaraathnd
You wait here,Eer moolpa untle
I feel fresh,Yenk ushaar anipundu
She is bored,Aaleg bore aavundu
He looks happy,Aaye kushid thojuve
They are fast,Akulu bega uller
We should meet,Nama thikkodu
You tell her,Eer aaleg panle
I will wait,Yaan kaapuve
She is quick,Aalu bega malpuva
He is strong,Aaye gatti
They are good,Akulu edde
You listen well,Eer edde kenpar
I am calm,Yaan shantha ulle
She is caring,Aalu kaalaji malpuva
He is sharp,Aaye tikshna
They are kind,Akulu dayanvither
We are okay,Nama edde ullayi
You keep trying,Eer prayathna malpondene uppule
I saw her,Yaan aalen thooye
He is rich,Aaye srimanthe
We should walk,Nama nadeyodu
You sit down,Eer tirt kulyer
I feel strong,Yenk gatti anipundu
She is smart,Aalu ushaar
He is funny,Aaye naga barpaavune
They are quiet,Akulu shanthoode uller
We are inside,Nama ulai ullayi
You stay safe,Eer surakshitha uppule
I need rest,Yenk visranthi bodi
She is helpful,Aalu sahaya malpuva
He is brave,Aaye dhairya
They are calm,Akulu shanthavaad uller
We must try,Nama prayathna malpaodu
You are late,Ireg porthu aathnd
I will stop,Yaan unthpe
She is fair,Aalu edde
He is gentle,Aaye mellane
They are weak,Akulu ashaktha
We are near,Nama kaikittal ullayi
You look upset,Eer bejard thojuvor
I feel sad,Yenk bejaraathnd
She is lazy,Aalu somberi
He is sleepy,Aayag jelpu barondndu
They are smiling,Akulu theliyonduLLer
We should plan,Nama thanta malpoyi
You are correct,Eer pandini sari
I found her,Yaan aalen thikkide
She is neat,Aalu nit
He is loyal,Aaye nambike ullaye
They are brave,Akulu dhairyavantharu
We must move,Nama povaodu
You sit here,Eer moolpa kulyer
He is shy,Aaye naachike ullaye
They are loud,Akulu gattid paaterver
We are fine,Nama edde ullayi
You stay calm,Eer shanthoode uppule
She is kind,Aalu dayaamayee
He is slow,Aaye mellane
They are smart,Akulu ushaar
We should play,Nama gobboyi
You come soon,Eer bega bale
I will go,Yaan pope
She is tall,Aalu thegge
He is short,Aaye giddane
They are fun,Akulu moji ullinakulu
We must work,Nama kelsa malpaodu
You are sweet,Eer laak ullar
I am fast,Yaan bega ulle
She is rich,Aalu srimanthi
He is poor,Aaye badave
They are strong,Akulu gatti
We should share,Nama paalidoli
You learn well,Eer edde kalpuvar
I love this,Yenk undu masth ishta
She is good,Aalu edde
He is rude,Aaye kopishte
They are clean,Akulu nit ullar
You wait outside,Eer pidayi kaapule
I am slow,Yaan mellane
They are cool,Akulu cool uller
We must rest,Nama visranthi dettonodu
You are here,Eer moolpa ullar
I feel nice,Yenk edde anipundu
She is sweet,Aalu laak ulla
He is caring,Aaye kaalaji ullaye
They are tired,Akulu susthaather
We are hungry,Yenkleg banji gumpu
You look great,Eer masth edde thojuvor
I will run,Yaan balipuve
She is silly,Aalu tharle
He is angry,Aaye kopad ulle
They are cute,Akulu muddu ullinakulu
You help her,Eer aaleg sahaya malple
I need food,Yenk vanaas bodi
She is happy,Aalu kushid ulla
You stay near,Eer kital uppule
I am happy,Yaan kushid ulle
She is busy,Aalu busy ulla
They are helpful,Akulu sahayakaru
You did great,Eer edde malthar
She is fine,Aalu ushaard ulla
He is smiling,Aaye theliyonduLLe
They are happy,Akulu kushid uller
You are right,Eer pandini sari
I am angry,Yenk kopa batthnd
She is fast,Aalu bega
He is bored,Aayag bore aavundu
They are funny,Akulu naga barpaavune
You stay home,Eer illad uppule
She is cute,Aalu muddu ulla
He is great,Aaye edde
They are okay,Akulu paravagilla
You did it,Eer unden malthar
I will help,Yaan sahaya malpe
She is clever,Aalu chalaki
He is nice,Aaye edde naramanye
We should sit,Nama kulyodu
She is small,Aalu yellya
He is big,Aaye malla
They are lazy,Akulu somberilu
We must join,Nama serodu
You keep going,Eer mundarisale
I feel weak,Yenk bala ijji anipundu
He is helpful,Aaye sahayake
They are poor,Akulu badaver
You wait now,Eer itte untle
I am shy,Yaan naachike ullaye
He is happy,Aaye kushid ulle
We should stay,Nama moolpa uppodu
I need peace,Yenk shanthi bodi
She is cool,Aalu cool ulla
They are neat,Akulu nit ullar
We are free,Nama swatantra ullayi
You learn fast,Eer bega kalpuvar
I am strong,Yaan gatti ulle
She is slow,Aalu mellane
He is cute,Aaye muddu
They are shy,Akulu naachike ullinakulu
We must plan,Nama thanta malpaodu
You are gentle,Eer mellane ullar
I will smile,Yaan thelipe
She is quiet,Aalu shanthavaad ulla
They are silly,Akulu tharle ullinakulu
We are smart,Nama ushaar ulla
You stay still,Eer avle unthule
I feel light,Yenk yellya anipundu
He is lazy,Aaye somberi
They are angry,Akulu kopad uller
We must stop,Nama unthodu
You are near,Eer kital ullar
I am quick,Yaan bega
We are clean,Nama clean ulla
I feel hot,Yenk becha aavundu
We must wait,Nama kaapodu
You come fast,Eer bega bale
You are ready,Eer tayar ullar
He is quick,Aaye bega malpuve
They are busy,Akulu busy uller
We must sleep,Nama jeppodu
You stay fine,Eer ushaard uppule
I am cold,Yenk chali aathnd
He is fair,Aaye edde
She is tired,Aalu susthaathal
We must run,Nama balipodu
He is good,Aaye edde Ulle
They are tall,Akulu udha uller
You must be happy,Eer kushith ullar andh
I need to clean my room,Yenk yenna room clean malpaodu
You have a big house,Ireg malla ill undu
You have a beautiful home,Ireg masth porluda ill undu
I am cutting down on sweets,Yaan teepi kammi malpondulle
Somebody help me,Yenk yerandaala sahaya malple
Go sit on the roof,Pood carcheda mitt kulyer
That was last week,Avu kaledina vaara ithnd
You are the best person I know,Yenk gothina edde janma eer
Dont even look at me,Yennan thoovodchi
She was born to dance,Aalu nartanakkaad puttinavu
That is not a pencil,Avu pencil att
Wash your hands before cooking,Aduge malpud dumbe kai dekkle
Pass me the spoon,Yenk spoon korle
Chop the onions finely,Neeruli sanna karthle
Peel the potatoes,Batate cheelile
Add some salt,Onchooru uppu paadle
Taste the soup,Soup ruchi thoole
Dont spill the milk,Per chelorchi
Boil the water,Neer urkalle
Turn off the stove,Stove off malple
Put the dishes in the sink,bajana sink-d paadle
Serve the food hot,Becha Becha  vanaas balasle
Wash the vegetables,Tharukaari dekkle
Peel and crush the garlic,Bollulli da choli dethed nekke malple
Add some lemon juice,Onchooru nimbe neer paadle
Break the egg carefully,thetti melaane pudaple
Add a pinch of sugar,Onchooru sakkare paadle
Roll the chapati,Chapathi lattile
Let it cool,Avu arapad
Increase the flame,flame jaasthi malple
Keep stirring,Kaladavondu uppule
Dont burn the garlic,Bollulli karnchavorchi
Bring me a plate,Yenk onji plate konale
Pour the juice,Juice paadle
Serve the salad,Salad balasle
Place the kajipu on the table,kajipu table-da mitt deele
Pass me the salt please,Dayamalthd yenk uppu korle
Take some more rice,Koodonchooru nuppu dettonle
Use a knife carefully,bisaathi jagerthed use manpule
Eat slowly,Mellaane tinle
Finish your vegetables,Tharakaari thind mugipule
Enjoy your meal,shokud vanaas malple
The food smells great,Vanasda parimala masth shok undu
Wash the dishes,baajana dekkle
Wipe the table,Table oresle
Clean the sink,Sink clean malple
Cover the food,Vanaas mucchile
Put the leftovers in the fridge,oridina vanas fridge-d deele
Dry the plates,Plate nungale
Sweep the kitchen floor,adigedha nela adiple
Dont waste water,Neer waste malporchi
Dont leave dirty plates,made paathre budpordchi
Take the strainer,Arane dettonle
Switch on the mixer,Mixer on malple
Put the kettle on,Kettle deele
Get me a clean bowl,Yenk shok da bowl korle
The kajipu is too spicy,kajipu masth kara undu
This dish is too salty,Ee vanaas masth uppu undu
The chicken is overcooked,Kori jaasthi beithend
The pasta is undercooked,Pasta beithiji
The food is delicious,Vanaas masth ruchi undu
Make the kajipu,kajipu malple
Can you drop me here,Yennanu moolpa budpara
Please drive safely,Dayamalthd ushaard gaadi budle
Is it far from here,Undu moolpard doora undaa
How much will it cost,Undek yeth Kaas aavu
Do you accept online payment,Eer online payment dettonvara
Please stop here,Dayamalthd moolpa untaale
Where does this bus go,Ee bus olpa popundu
What time is the next bus,Bakkada bus yeth ganteg
Where can I buy a ticket,Ticket olpa dettonoli
Is this seat reserved,Ee seat reserve aathundaa
Can you show me on the map,Map-d yenk thojpaavara
What do you recommend,Eer daada panpar
Can I have the bill please,Bill korpara
I lost my passport,Yenna passport dakdh pothundu
Can you take a photo of me,Yenna onji photo dettonvara
What is the best time to visit this place,Ee jaagag poyere vaa porthu yedde
I am here for tourism,Yaan thirgyere baide
How much is the entrance fee,Ulai poyer yeth kaas
Can I take pictures here,Moolpa photo deppoliya
How long will it take to walk there,Aade nadapere yeth porthu bodu
Sorry  I am late,"Sorry, yenk porthu aandu"
Please repeat once more,Dayamalthd koodonji sarti panle
When is the assignment due,Assignment yepag korodu
Can I borrow your notes,Irena notes dettonoliya
Are we having a test today,Namak ini parikshe undaa
Can I leave early today,Yaan ini bega povoliya
Do we have a class tomorrow,Yelle  namak class undaa
Is attendance compulsory,Attendance bodenaa
Can I ask a question,Yaan onji prashne kenoliya
Where is the seminar hall,Seminar hall olpa undu
Where is the notice board,Notice board olpa undu
How do I apply for a leave,Raje-g yencha apply malpuni
Who is the class representative,Class representative yer
Is this important for the exam,Undu exam-g mukhyanaa
Where can I collect my hall ticket,Hall ticket olpa thikkundu
Best wishes on your wedding day,Madimeda shubhshaya
You both look perfect together,Nikulu radd jana shok ullar ottige
Enjoy the party,Party-d gammath malpule
The decorations are beautiful,Decorations masth shok thojundu
The dance floor is open,Dance floor open undu
Happy married life,Kushida madime jeevana
The groom looks so handsome,Madimaye masth porlu thojuve
The music is amazing,Music masth shokundu
You both look so happy,Nikul radd jana masth kushit ullar
Please hurry up,Dayamalthd bega malple
check the quality,Quality check malple
No bargaining fixed price,Kraya kammi ijji fixed rate
Can I get a carry bag,Carry bag thikkoliya
should i go,ಯಾನ್ ಪೊವೊಡಾ
master,ಮಾಸ್ಟರ್
Place the curry on the table,ಕಜಿಪುನ್ ಮೇಜಿದ ಮಿತ್ತ್ ದೀಲೆ
The curry is too spicy,ಕಜಿಪು ಮಸ್ತ್ ಖಾರ ಉಂಡು
Make the curry,ಕಜಿಪು ಮಲ್ಪುಲೆ
What's the weather in Mangalore?,Kudla-d havamana yencha undu?
Tell me today's weather.,Initha havamana yencha undu panle.
Is it raining in Udupi right now?,Udupi-d itte barsa barond unda?
What is the temperature in Bangalore now?,Bangalore-d itte thapamaana yeth undu?
Will it be sunny tomorrow?,yelle bolkiri uppuva
How humid is it in Delhi today?,Delhi-d ini thodi yeth undu?
Give me the weather update for Mumbai.,Mumbai-da havamana update korle.
Is it going to be windy this evening?,Ini baiyag gaali beejuva
Check the weather for the weekend.,Weekend-da havamana check malpule.
What's the forecast for Kasaragod tomorrow?,Yelle Kasaragod-da havamana yencha undu?
Please tell me whether it will rain in Mangalore tomorrow evening because I have to travel.,Yelle baiyag Mangalore-d barsa barpunda panle yenk travel malpare undu.
Check if it will rain in Udupi before I leave for college.,Yaan college-g popinerd dumbu Udupi-d barsa barpunda check malpule.
Tell me the weather in Puttur because I am planning a bike trip.,Puttur-da havamana panle yaan bike trip plan malthonde.
I need to know if it will be cold in Manipal tomorrow morning because I have an early class.,Yelle kaande Manipal-d chali ippuva nd  yenk theripale daye panda yenk yelle kaandeda class undu.
Let me know if there will be a storm tonight since I have to walk home.,Ini raathre birugaali barpunda dayeg panda yaan nadathond illag povod.
What will the weather be like in Bangalore when I land this evening?,Baiyag yaan Bangalore-g muttunaga havamana yencha uppu?
Check the weather in Mangalore before I decide whether to carry an umbrella.,Kode kondu popine nishchaya malpunerd dumbe Mangalore-da havamana yencha undu nd check malpule.
Will it be hot in Delhi in the afternoon because I have an outdoor event?,Delhi-d Madhyanna dombu uppuva daye panda yenk avl  karyakrama undu.
Tell me tomorrow's weather in Mumbai since I have a flight in the morning.,Yelle Mumbai-da havamana panle kaande yenk flight undu.
I want to know if it will rain this weekend because we planned a picnic.,Ee weekend barsa barpunda nd panle daye panda nama picnic plan  manda
What is the wind speed in Udupi right now?,Itte Udupi-d gaalida vega yeth undu?
Will there be fog in Manipal early morning tomorrow?,Yelle kaande Manipal-d maindh uppuva
Should I carry a raincoat to Mangalore today?,Ini Kudla-g popunaga raincoat kondu podara?
How is the weather looking for tonight?,Ini raathre havamana yencha kanpundu?
Tell me if it's safe to travel to Kasaragod today because of the rain warning.,Barsada warning ittinard Kasaragod-g travel malpuni safe-aa panle.
What's the weather like in Mangalore right now?,Mangalore-d itte havamana yencha undu?
What's the weather like in Udupi right now?,Udupi-d itte havamana yencha undu?
What's the weather like in Bangalore right now?,Bangalore-d itte havamana yencha undu?
What's the weather like in Delhi right now?,Delhi-d itte havamana yencha undu?
What's the weather like in Mumbai right now?,Mumbai-d itte havamana yencha undu?
What's the weather like in Kasaragod right now?,Kasaragod-d itte havamana yencha undu?
Play music on Spotify.,Spotify-d paata paadule.
Open Spotify.,Spotify open malpule.
Play some Tulu songs.,Kaikonji Tulu paatelen paadule.
Play a relaxing playlist.,Onji samadhana apina playlist paadule.
Pause the music.,Paata pause malpule.
Skip this song.,Ee paaten skip malpule.
Play the next track.,Bukkada track paadule.
Search for a song on Spotify.,Spotify-d onji paaten naadle.
Play devotional songs on Spotify.,Spotify-d bhakthi geethelen paadule.
Open Spotify and play some Kannada songs.,Spotify open malth Kannada paatelen paadule.
Play Tulu songs on Spotify because I am driving home.,Spotify-d Tulu paatelen paadule dayegand yaan illag drive malthonde.
Play a relaxing playlist on Spotify before I sleep.,Yaan yedepard dumbe Spotify-d onji relax playlist paadule.
Play some workout songs on Spotify because I am going to the gym.,Yaan gym-g popinard Spotify-d workout paatelen paadule.
Open Spotify and play devotional songs when I start my morning prayers.,Kaande pooje suru malpunaga Spotify open malth bhakthi geethelen paadule.
Play something calm on Spotify since I have a headache.,Yenk thare beene undu Spotify-d shanthavaad uppuna paata paadule.
Play my favourite playlist on Spotify before the guests arrive.,Bannager bathard dumbe Spotify-d yenna ishtada playlist paadule.
Play old Tulu folk songs on Spotify because my grandmother wants to listen.,Daddig paata kenere undu Spotify-d parath Tulu paatelen paadule.
Pause the music on Spotify because someone is calling me.,Spotify-d paata pause malpule yerno phone barpundu.
Play romantic songs on Spotify after dinner.,Vanass kaled bokka Spotify-d romantic paatelen paadule.
Play the same song again on Spotify.,Spotify-d anchine paaten kooda onji sarthi paadule.
Increase the volume on Spotify.,Spotify-d volume hechha malpule.
Play a podcast on Spotify instead of music.,Spotify-d paatada badal podcast paadule.
Play travel songs on Spotify because we are going on a road trip tomorrow.,Yelle yaan travel popinarada Spotify-d travel paatelen paadule.
Shuffle my playlist on Spotify.,Spotify-d yenna playlist-n shuffle malpule.
Play Yakshagana music on Spotify.,Spotify-d Yakshagana paatelen paadule.
Open the calculator.,Calculator open malpule.
What is 25 plus 47?,25 koodi 47 yeth apundu?
Calculate 15 times 8.,15 guna 8 calculation malpule.
What is 120 divided by 4?,120-n 4-d paalu malthnda yeth apundu?
Subtract 45 from 100.,100-d 45-n kaledanda yeth?
What is the square root of 81?,81-da square root da lekkalike yeth?
Calculate 12 percent of 500.,500-da 12 percent calculation malpule.
Open the calculator because I need to check my monthly expenses.,Tingalda karchu check malpare undu calculator open malpule.
Calculate 250 plus 375 before I finalize the budget.,Budget nishchaya malpunard dumbe 250 koodi 375 lekka malpule.
What is 18 times 24 because I need it for my homework?,Homework malpare undu 18 guna 24 yeth apundu panle.
Divide 900 by 12 since I'm splitting the bill with friends.,Dosthulla bill paalu malpare undu 900-n 12-d bhagisale.
"Calculate my total marks by adding 85, 90 and 78.","85, 90 bokka 78-n koodad yenna total marks lekka malpule."
What is 7 squared?,7-da square yeth apundu?
Open the calculator before the shopkeeper gives me the final price.,Angadi aai kadaisi bele panpard dumbe calculator open malpule.
Add 15000 and 22000 for the monthly budget.,Tingalda budget-g 15000 bokka 22000-n koodale.
Calculate the discount if the price is 2000 and discount is 20 percent.,Bele 2000 bokka 20 percent discount ithnda discount lekka malpule.
What is 999 minus 456?,999-d 456-n kaledanda yeth apundu?
Multiply 45 by 6 because I need to convert units.,Unit convert malpare undu 45-n 6-d guna malpule.
Open notepad.,Notepad open malpule.
Close notepad.,Notepad close malpule.
Open chrome.,Chrome open malpule.
Open chrome and search for today's news.,Chrome open malth initha sudhi naadle.
Open the camera.,Camera open malpule.
Close the camera.,Camera close malpule.
Open notepad because I need to write down some notes.,Sannada vishaya barepare undu Notepad open malpule.
Open chrome before my online class starts.,Online class suru aapinard dumbe Chrome open malpule.
Open the camera because I want to take a photo of the sunset.,Surya buroline photo deppere undu Camera open malpule.
Close chrome after I finish checking my email.,Email check malth bokka Chrome close malpule.
Open notepad and write down my shopping list.,Notepad open malth samanuda list barele.
Open chrome and search for the nearest hospital because it's urgent.,Bejaratha vishaya undu bega Chrome open malth hathirada aaspitre naadle.
Take a photo before the guests arrive.,Bannager barpard dumbe photo deppule.
Open notepad since I need to save this phone number.,Ee phone number save malpare Notepad open malpule.
Minimize all windows.,Maatha windowlen minimize malpule.
Open file manager.,File manager open malpule.
Take a screenshot.,Onji screenshot deppule.
Open chrome and go to Gmail.,Chrome open malth Gmail-g pole.
Close all open applications because my laptop is running slow.,Laptop slow aathundu maatha applen close malpule.
Open the camera to record a short video for my project.,Project-g onji yelyada video thegeyere Camera open malpule.
Open YouTube and search for Tulu songs because I want to relax.,Samadhana gollere YouTube open malth Tulu paatelen naadle.
"Before I sleep, open YouTube and play devotional songs.",Yedepard dumbe YouTube open malth bhakthi geethelen paadule.
Open YouTube and search for cooking tutorials because I want to try a new recipe.,Posatha adige kalpare YouTube open malth adigeda video naadle.
Search YouTube for yesterday's cricket match highlights.,Kodanda cricket match da highlights-n YouTube-d naadle.
Open YouTube when I finish my homework so I can watch cartoons.,Homework poora aayin bokka cartoon thuyere YouTube open malpule.
Play the latest Tulu movie trailer on YouTube.,YouTube-d posa Tulu cinemada trailer paadule.
Open YouTube and search for machine learning tutorials because I have an exam next week.,Yelle vaara parikshe undu machine learning padhapulen YouTube-d naadle.
Search YouTube for workout videos before I go to the gym.,Gym-g popinard dumbe workout video-n YouTube-d naadle.
Open YouTube and play Yakshagana performances since my father wants to watch.,Ammag thuyere YouTube open malth Yakshagana paadule.
Search YouTube for how to fix a flat tyre because my bike broke down.,Bike puncture aathundu flat tyre sarpa malpunen YouTube-d naadle.
Search Google for the nearest hospital because it's an emergency.,Emergency undu hathirada aaspitre-n Google-d naadle.
Search Google for tomorrow's train timings because I need to catch a train.,Rail pathered undu yelle rail time-n Google-d naadle.
Google the meaning of this word because I don't understand it.,Artha aathiji ee shabdada arthan Google-d naadle.
Search Google for good restaurants near me before we decide where to eat.,Oota khachith malpunard dumbe Google-d yelle yedde hotel naadle.
Search Google for the college admission dates since the deadline is close.,Kadaisi din hathira barpundu college admission dinathen Google-d naadle.
Search Google for the exchange rate because I'm planning to travel abroad.,Videsha-g popina aalochane undu exchange rate-n Google-d naadle.
Google search for the pin code of this area.,Ee jageda pin code Google search malpule.
Search Google for today's petrol price before I fill my tank.,Petrol paadnard dumbe initha petrol bele Google-d naadle.
Search Google for the symptoms of fever because I'm feeling unwell.,Meyyi usharidji jorada lakshanalen Google-d naadle.
Tell me about artificial intelligence because I have an exam tomorrow.,Yelle parikshe undu artificial intelligence bagge yenk panle.
Explain photosynthesis to me before my biology test.,Biology pariksherd dumbe photosynthesis bagge artha malpale.
What is climate change and why does it matter?,Havamana badalavane danna bokka auda mukhyathe yenchina?
Tell me about the history of Tulu Nadu since I'm writing a project.,Project barevonde Tulu naad-da ithihasada bagge panle.
Explain how a computer processor works because I'm curious.,Aasakthi undu computer processor yencha kelasa malpundu panle.
What is the capital of Karnataka?,Karnataka-da rajadhani oodu?
Tell me about the solar system because my son asked me a question.,Mage kende sowra mandala bagge panle.
Explain what machine learning is before my interview tomorrow.,Yelle interview undu machine learning danna yenk theripale.
What causes earthquakes?,Bhoo kampana dayeg apundu?
Set an alarm for 7 am tomorrow because I have a train to catch.,Train pathered undu yelle kaande 7 ghante-g alarm deele.
Wake me up at 6 in the morning before college starts.,College suru apinard dumbe kaande 6 ghante-g yennan lakkele.
Set an alarm for every weekday morning because I have classes.,Class ithinard varada kelsa dina kaande alarm deele.
Set an alarm for 5:30 am tomorrow since I have to leave early for a trip.,Trip-g bega popinard yelle kaande 5:30-g alarm deele.
Remind me at 9 pm to take my medicine.,Marthulenge thinnere raathre 9 ghante-g yenk nenpu malpule.
Set an alarm for 6:45 because I don't want to miss the bus.,Bus miss aavaradji 6:45-g alarm deele.
Wake me up at 4 am tomorrow because I have an early flight.,Bega flight undu yelle kaande 4 ghante-g lakkele.
Set a daily alarm at 6 am for my morning walk.,Kaande nadapere kelsa dina kaande 6 ghante-g alarm deele.
Cancel the alarm I set for tomorrow morning.,Yelle kaandeda alarm-n cancel malpule.
Lock the door.,Baakil lock malpule.
Unlock the door.,Baakil unlock malpule.
Lock the door before I leave the house.,Illard pidai popina dumbu baakil lock malpule.
Unlock the door because I forgot my keys inside.,Chabi ullai bukkude baakil unlock malpule.
Lock the door when I go to sleep.,Yedepere popinaga baakil lock malpule.
Unlock the door since a guest has arrived.,Bannager bather baakil unlock malpule.
Lock the front door after everyone leaves for work.,Kelsag boyina bokka yeduru baakil lock malpule.
Check if the door is locked before I go to bed.,Yedepard dumbe baakil lock aathunda thule.
Unlock the door because I just came back home.,Itte illag bathede baakil unlock malpule.
Lock the door immediately because I heard a strange noise outside.,Pidayi shabdha kenna thakshanane baakil lock malpule.
Is the door locked right now?,Baakil itte lock aathunda?
Unlock the door for the delivery person.,Delivery korre baathinaayeg baakil open malpule.
Lock the door and confirm once it's done.,Baakil lock malth bokka confirm malpule.
Keep the door locked until I return in the evening.,Baiyag yaan barpuna mutta baakil lock deele.
Unlock the door before my friends come over.,Dosthilu barpuna dumbu baakil unlock malpule.
"""

def clean_text(text):
    text = str(text).strip()
    text = re.sub(r'["\']', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def main():
    # 1. Parse user dataset
    df_user = pd.read_csv(io.StringIO(USER_DATASET_TEXT))
    df_user = df_user.rename(columns={"ENGLISH": "English", "ENGLISH_TULU": "Tulu"})
    df_user["English"] = df_user["English"].apply(clean_text)
    df_user["Tulu"] = df_user["Tulu"].apply(clean_text)
    df_user = df_user.dropna(subset=["English", "Tulu"])
    df_user = df_user[(df_user["English"] != "") & (df_user["Tulu"] != "")]

    print(f"Parsed {len(df_user)} rows from user data.")

    # 2. Load existing clean_dataset.csv if exists
    if CLEAN_DATASET_PATH.exists():
        df_existing = pd.read_csv(CLEAN_DATASET_PATH)
        df_existing["English"] = df_existing["English"].apply(clean_text)
        df_existing["Tulu"] = df_existing["Tulu"].apply(clean_text)
        print(f"Existing clean dataset has {len(df_existing)} pairs.")
    else:
        df_existing = pd.DataFrame(columns=["English", "Tulu"])

    # 3. Combine and Deduplicate
    combined = pd.concat([df_existing, df_user], ignore_index=True)
    combined["en_lower"] = combined["English"].str.lower().str.replace(r'[^\w\s]', '', regex=True)
    combined["tu_lower"] = combined["Tulu"].str.lower().str.replace(r'[^\w\s]', '', regex=True)
    
    # Drop duplicates
    deduped = combined.drop_duplicates(subset=["en_lower", "tu_lower"]).drop(columns=["en_lower", "tu_lower"])
    print(f"Total merged & deduplicated pairs: {len(deduped)}")

    # 4. Save to files
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    deduped[["English", "Tulu"]].to_csv(CLEAN_DATASET_PATH, index=False, encoding="utf-8")
    deduped[["English", "Tulu"]].to_csv(EXPANDED_DATASET_PATH, index=False, encoding="utf-8")
    print(f"Saved merged dataset to: {CLEAN_DATASET_PATH}")

    # 5. Rebuild vocabulary mappings
    VOCAB_DIR.mkdir(parents=True, exist_ok=True)
    en_words = set()
    tu_words = set()

    for _, row in deduped.iterrows():
        en_toks = re.findall(r'\b\w+\b', str(row["English"]).lower())
        tu_toks = re.findall(r'\b\w+\b', str(row["Tulu"]).lower())
        en_words.update(en_toks)
        tu_words.update(tu_toks)

    en_vocab = {w: idx + 4 for idx, w in enumerate(sorted(en_words))}
    en_vocab["<pad>"] = 0
    en_vocab["<bos>"] = 1
    en_vocab["<eos>"] = 2
    en_vocab["<unk>"] = 3

    tu_vocab = {w: idx + 4 for idx, w in enumerate(sorted(tu_words))}
    tu_vocab["<pad>"] = 0
    tu_vocab["<bos>"] = 1
    tu_vocab["<eos>"] = 2
    tu_vocab["<unk>"] = 3

    with open(VOCAB_DIR / "english_vocab.json", "w", encoding="utf-8") as f:
        json.dump(en_vocab, f, ensure_ascii=False, indent=2)

    with open(VOCAB_DIR / "tulu_vocab.json", "w", encoding="utf-8") as f:
        json.dump(tu_vocab, f, ensure_ascii=False, indent=2)

    print(f"Vocabulary updated -> English: {len(en_vocab)} tokens, Tulu: {len(tu_vocab)} tokens")

if __name__ == "__main__":
    main()
