from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Category, Base, Item ,User
 
engine = create_engine('sqlite:///category.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


User1 = User(name="admin", email="tinnyTim@udacity.com",
             picture='https://image.flaticon.com/icons/svg/17/17004.svg')
session.add(User1)
session.commit()

category1 = Category(user_id=1,name = "drama")

session.add(category1)
session.commit()

Item1 = Item(user_id=1,name = "Bohemian Rhapsodyr", description = """Freddie
             Mercury -- the lead singer of Queen -- defies stereotypes and 
             convention to become one of history's most beloved entertainers. 
             The band's revolutionary sound and popular songs lead to Queen's
             meteoric rise in the 1970s. After leaving the group to pursue a 
             solo career, Mercury reunites with Queen for the benefit concert
             Live Aid -- resulting in one of the greatest performances in rock
             'n' roll history.""", category = category1)
session.add(Item1)
session.commit()

Item2 = Item(user_id=1,name = "Dunkirk", description = """In May 1940, Germany
             advanced into France, trapping Allied troops on the beaches of
             Dunkirk.Under air and ground cover from British and French forces,
             troopswere slowly and methodically evacuated from the beach using
             every serviceable naval and civilian vessel that could be found. 
             At the end of this heroic mission, 330,000 French, 
             British, Belgian and Dutch soldiers were safely evacuated.""", 
             category = category1)
session.add(Item2)
session.commit()

Item3 = Item(user_id=1,name = "First Man", description = """Hoping to reach the
             moon by the end of the decade, NASA plans a 
             series of extremely dangerous, unprecedented missions in the early
             1960s. Engineer Neil Armstrong joins the 
             space program, spending years in training and risking his life
             during test flights. On July 16, 1969, the 
             nation and world watch in wonder as Armstrong and fellow astronauts 
             Buzz Aldrin and Michael Collins embark 
             on the historic Apollo 11 spaceflight.""", category = category1)
session.add(Item3)
session.commit()

Item4 = Item(user_id=1,name = "12 Years a Slave", description = """In the years
             before the Civil War, Solomon Northup (Chiwetel Ejiofor), 
             a free black man from upstate New York, is kidnapped and sold into
             slavery in the South. Subjected to the cruelty of one malevolent owner 
             (Michael Fassbender), he also finds unexpected kindness from
             another, as he struggles continually to 
             survive and maintain some of his dignity.
             Then in the 12th year of the disheartening ordeal, a chance meeting
             with an abolitionist from Canada changes Solomon's life forever."""
             , category = category1)
session.add(Item4)
session.commit()

Item5 = Item(user_id=1,name = "Manchester by the Sea", description = """After
             the death of his older brother Joe, Lee Chandler (Casey Affleck) is
             shocked that Joe has made him sole guardian of his teenage nephew
             Patrick. Taking leave of his job as a janitor in Boston,
             Lee reluctantly returns to Manchester-by-the-Sea, the fishing 
             village where his working-class family has lived for generations. 
             There, he is forced to deal with a past that separated him from 
             his wife, Randi (Michelle Williams), 
             and the community where he was born and raised.""", category = category1)
session.add(Item5)
session.commit()


category2 = Category(user_id=1,name = "comedy ")

session.add(category2)
session.commit()

Item1 = Item(user_id=1,name = "The Hustle", description = """Josephine
             Chesterfield is a 
             glamorous, seductive British woman who has a penchant
             for defrauding gullible men out of their
             money. Into her well-ordered, meticulous world comes Penny Rust
             , a cunning and fun-loving Australian 
             woman who lives to swindle unsuspecting marks. Despite their
             different methods, the two grifters soon join forces for the 
             ultimate score
             -- a young and naive tech billionaire in the South of France.""",
             category = category2)
session.add(Item1)
session.commit()

Item2 = Item(user_id=1,name = "The Hangover", description = """Two days before 
             his wedding, Doug (Justin Bartha) and three friends (Bradley Cooper
             , Ed Helms, Zach Galifianakis)
             drive to Las Vegas for a wild and memorable stag
             party. In fact, when the three groomsmen
             wake up the next morning, they can't remember
             a thing; nor can they find Doug. With little
             time to spare, the three hazy pals try to re-trace
             their steps and find Doug so they can
             get him back to Los Angeles in time to walk 
             down the aisle.""", category = category2)
session.add(Item2)
session.commit()

Item3 = Item(user_id=1,name = "Superbad", description = """Two inseparable best
             friends navigate the last weeks
             of high school and are invited to a gigantic house party. Together
             with their nerdy friend,
             they spend a long day trying to score enough alcohol to supply the
             party and inebriate two girls
             in order to kick-start their sex lives before they go off to 
             college. Their quest is complicated
             after one of them falls in with two inept cops who are determined
             to show him a good time.""", category = category2)
session.add(Item3)
session.commit()

Item4 = Item(user_id=1,name = "Bridesmaids", description = """Annie
             (Kristen Wiig) is a single woman whose own life
             is a mess, but when she learns that her lifelong best friend,
             Lillian(Maya Rudolph), is engaged, she 
             has no choice but to serve as the maid of honor. Though lovelorn
             and almost penniless, Annie, nevertheless
             , winds her way through the strange and expensive rituals
             associated with her job as the bride's go-to gal.
             Determined to make things perfect, she gamely leads Lillian and
             the other bridesmaids down the wild road to the wedding.""", 
             category = category2)
session.add(Item4)
session.commit()

Item5 = Item(user_id=1,name = "Step Brothers", description = """Brennan Huff 
             (Will Ferrell) and Dale Doback (John C. Reilly)
         have one thing in common: they are both lazy, unemployed leeches
         who still live with their parents. When Brennan's mother and Dale's
         father marry and move in together, it turns the overgrown boys'
         world upside down. Their insane rivalry and narcissism pull the
         new family apart, 
         forcing them to work together to reunite their parents.""", category = category2)
session.add(Item5)
session.commit()






print ("added menu items!")