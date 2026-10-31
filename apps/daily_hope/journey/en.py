"""Daily Hope in English: 21 short emails, one a day. Verses are from the
World English Bible (ebible.org/engwebp), copied by script, never retyped."""

DAYS = {
    1: {
        'title': 'Hope can start small',
        'opening': (
            'Maybe you signed up for this between other things, on a bus or at the end of a long day with your phone almost out of battery. For the next 21 days, one short email will come each day. Each one has a verse, a few lines about it and one small thing to try.\n\n'
            'Here is today’s. Wherever you are, breathe in slowly for 4 counts and out for 6, five times. It takes about a minute. Then write one honest sentence about how you are today, in your phone’s notes or on a piece of paper. Nobody else needs to read it.'
        ),
        'verse': 'Now may the God of hope fill you with all joy and peace in believing, that you may abound in hope in the power of the Holy Spirit.',
        'verse_ref': 'Romans 15:13',
        'after': 'Paul calls God “the God of hope”. Hope comes from God, so it does not depend on how strong you feel this morning. Paul says joy and peace come “in believing”, and believing can start very small: turning to God once today and telling him how you are.',
        'question': 'What is weighing on you today that you could tell God in one sentence?',
        'prayer': 'God of hope, you know how I am today, even the parts I can’t explain. Fill me with your peace as I trust you, a little at a time. Thank you that I can come to you through Jesus. Amen.',
    },
    2: {
        'title': 'When others seem ahead',
        'opening': (
            'You open your phone and someone you went to school with has a new job or a new baby. You close the app feeling a little smaller than you did five minutes ago. Most people know this feeling. Social media shows the best day of everyone’s year, and we hold it up against an ordinary day of our own.\n\n'
            'Today, the next time you catch yourself comparing, put the phone face down for ten minutes. Then write down one thing you learned or got through in the past year that nobody posted about.'
        ),
        'verse': 'He has made everything beautiful in its time. He has also set eternity in their hearts, yet so that man can’t find out the work that God has done from the beginning even to the end.',
        'verse_ref': 'Ecclesiastes 3:11',
        'after': 'The writer of Ecclesiastes watched people work, wait, grieve and start over, and he saw that everything has its time. Your life has its own seasons. Some of what God is doing in you, like learning patience or learning to ask for help, never shows up in a photo. It still counts. Being slower than someone else at one thing says nothing about what you are worth to God.',
        'question': 'Whose life have you been measuring yourself against lately?',
        'prayer': 'Lord, when I compare my life with other people’s, I feel late. Help me trust your timing for my life and take the next step in front of me. In Jesus’ name, amen.',
    },
    3: {
        'title': 'When you are tired',
        'opening': (
            'It’s the end of the day. The dishes are still in the sink, there are messages you haven’t answered, and you are too tired to start anything. Sleep helps a little, but some tiredness stays even after a full night. It comes from carrying a lot for a long time: work, family, money and worry.\n\n'
            'Today, pick one thing on your list that can wait until tomorrow, and let it wait. Use the time for rest. Sit down for 15 minutes with something to drink and no phone, or go to bed half an hour earlier.'
        ),
        'verse': 'Come to me, all you who labor and are heavily burdened, and I will give you rest.',
        'verse_ref': 'Matthew 11:28',
        'after': (
            'Jesus said this to ordinary people worn out by work and by heavy religious rules. His answer to their tiredness was an invitation: come to me. You can come as you are, and tell him how tired you are in one sentence, on the bus or lying in bed.\n\n'
            'If you have felt exhausted or low most days for a few weeks, see a doctor as well. Tiredness can have causes that a doctor can help with.'
        ),
        'question': 'What have you been carrying that is wearing you out?',
        'prayer': 'Jesus, I’m tired. I come to you as I am. Give me rest, and show me one thing I can put down today. Amen.',
    },
    4: {
        'title': 'When worry will not stop',
        'opening': (
            'You lie down and your mind starts running. What if the test results are bad? What if I can’t pay the rent this month? Worry tends to repeat the same few thoughts, and each one feels urgent.\n\n'
            'Today, try a five-minute worry list. Set a timer and write down everything you are worried about. Next to each worry, write one small next step, or “not today” if there is nothing you can do yet. Then pray through the list, one line at a time.'
        ),
        'verse': 'In nothing be anxious, but in everything, by prayer and petition with thanksgiving, let your requests be made known to God. And the peace of God, which surpasses all understanding, will guard your hearts and your thoughts in Christ Jesus.',
        'verse_ref': 'Philippians 4:6-7',
        'after': 'Paul wrote these words from prison, so he knew about worry. His advice is practical: tell God each thing specifically, and thank him for something while you do. He says God’s peace “surpasses all understanding”. It can come before the problem is solved. Prayer goes alongside the practical steps, so you can pray about a worry and still call the doctor or talk to your boss.',
        'question': 'Which worry has been going round in your mind this week?',
        'prayer': 'Father, you know what I’m worried about. I bring each worry to you by name. Guard my heart and my thoughts with your peace, in Christ Jesus. Amen.',
    },
    5: {
        'title': 'What you are worth to God',
        'opening': (
            'Maybe a parent or a teacher once told you that you could do better, or that you were too much. Years later you still hear it when you make a mistake. A lot of us measure our worth by how well we did today, and on a bad day it drops.\n\n'
            'Today, write down one harsh sentence you often say to yourself. Under it, write what you would say to a friend who said that about themselves. Read the second sentence out loud once.'
        ),
        'verse': 'I will give thanks to you, for I am fearfully and wonderfully made. Your works are wonderful. My soul knows that very well.',
        'verse_ref': 'Psalm 139:14',
        'after': 'When David wrote that he was “fearfully and wonderfully made”, he was thanking God for making him, before any list of things he had done. God valued you before you did anything right or wrong, and a bad day cannot change that. You can keep working on things in your life from there, without first having to earn God’s love.',
        'question': 'What do you tell yourself when you make a mistake?',
        'prayer': 'God, thank you for making me. When I measure myself by how well I did today, help me remember that you loved me first, and showed it in Jesus. Amen.',
    },
    6: {
        'title': 'When you don’t know what’s next',
        'opening': (
            'You might be deciding whether to leave a job, or waiting to hear back about something important. You have prayed about it and no clear answer has come. Not knowing what’s next can make every day feel unsettled.\n\n'
            'Today, take 10 minutes with a piece of paper. Write the decision at the top. Under it, write one next step you can take this week, however small, like sending one email or asking one person who has been through it.'
        ),
        'verse': 'Trust in the LORD with all your heart, and don’t lean on your own understanding. In all your ways acknowledge him, and he will make your paths straight.',
        'verse_ref': 'Proverbs 3:5-6',
        'after': 'Proverbs asks us to trust the Lord “with all your heart” and to acknowledge him “in all your ways”, and it promises that he will make your paths straight. He rarely shows the whole route at once. Most people find their way one step at a time, praying as they go and listening to people who know them well. When you can’t see far ahead, the next step is usually enough to work with.',
        'question': 'What is one small step you can take this week?',
        'prayer': 'Lord, I don’t know what’s next. I trust you with this decision. Show me the next step and help me take it. In Jesus’ name, amen.',
    },
    7: {
        'title': 'One week in',
        'opening': (
            'This is your seventh Daily Hope email, so you are one week in. Before you read on, think back over the past seven days. Some of them may have been hard. You still got up on most of them, and you opened this email today.\n\n'
            'Today, take five minutes and write down a few things you got through this week. Small ones count, like “made dinner on Wednesday” or “called my mom”.'
        ),
        'verse': 'It is because of the LORD’s loving kindnesses that we are not consumed, because his mercies don’t fail. They are new every morning. Great is your faithfulness.',
        'verse_ref': 'Lamentations 3:22-23',
        'after': 'The writer of Lamentations had watched his city fall. In the middle of that grief he wrote that God’s mercies are new every morning. He noticed God’s faithfulness while things were still hard, one morning at a time. Looking back at your week, you may notice it too, in help that came at the right time or in enough strength for one more day.',
        'question': 'Where did you see God’s help this past week?',
        'prayer': 'Lord, thank you for carrying me through this week. Thank you that your mercies will be new tomorrow morning too. Help me notice your care in small things. Through Jesus, amen.',
    },
    8: {
        'title': 'When nothing seems to change',
        'opening': (
            'You have been trying for months to find a job, or to break a habit, and you keep ending up in the same place. You pray about it, and nothing seems to move. That is discouraging, and it can make you want to stop trying.\n\n'
            'Today, look for a change that is easy to miss. Compare your life now with six months ago and write down one thing that is different, even slightly: something you handle a little better, or something you understand now that you didn’t then.'
        ),
        'verse': 'Let endurance have its perfect work, that you may be perfect and complete, lacking in nothing.',
        'verse_ref': 'James 1:4',
        'after': 'James wrote to Christians going through hard times. He says endurance has a “perfect work”: staying with something hard slowly makes us mature and complete. Growth often feels like repetition while it is happening. You face the same situation again, and each time you respond a little differently. That is real progress, even when nobody else can see it.',
        'question': 'Where in your life do you feel stuck right now?',
        'prayer': 'Lord, I feel stuck. Help me keep going, and help me see what you are doing in me while I wait. In Jesus’ name, amen.',
    },
    9: {
        'title': 'When guilt stays with you',
        'opening': (
            'There may be a moment you keep replaying, like something you said in anger or a time you weren’t there for someone. You apologized, or you never did, and it still comes back when you’re trying to sleep. Guilt is useful when it shows you something you can put right. After that, it only weighs you down.\n\n'
            'Today, if there is something you can put right, take one step, like sending an apology or paying something back. If there is nothing left to do, tell God about it once, plainly, in your own words.'
        ),
        'verse': 'If we confess our sins, he is faithful and righteous to forgive us the sins and to cleanse us from all unrighteousness.',
        'verse_ref': '1 John 1:9',
        'after': (
            'John writes that God is “faithful and righteous to forgive”. Forgiveness rests on who God is and on what Jesus has done, so you can stop replaying what God has already forgiven.\n\n'
            'Some guilt comes with depression or anxiety and has little to do with anything you did. If you feel guilty most days, talk to a doctor or counselor about it.'
        ),
        'question': 'What are you still holding against yourself?',
        'prayer': 'Father, you know what I keep replaying. I bring it to you. Thank you that you forgive through Jesus. Help me accept your forgiveness and put this down. Amen.',
    },
    10: {
        'title': 'When you feel alone',
        'opening': (
            'You can feel alone in a full room, at a family dinner or in a group chat that keeps buzzing. Everyone is talking, and nobody seems to notice how you really are. Loneliness is common, and it hurts.\n\n'
            'Today, send one short message to someone you trust, like “Can we talk this week?” or “I’ve been having a hard time lately.” It takes a minute, and it gives them a chance to be there for you.'
        ),
        'verse': 'The LORD is near to those who have a broken heart, and saves those who have a crushed spirit.',
        'verse_ref': 'Psalm 34:18',
        'after': (
            'David wrote this psalm after a frightening time in his life. He says the Lord is near to people with a broken heart. God comes close when you are low, before you feel better. He often helps through people too, so reaching out to one person is part of how loneliness starts to ease.\n\n'
            'If you have felt alone and low for weeks, talk to a doctor or counselor. If you are thinking of ending your life, call a crisis line in your country now. You can find one at hopebegins.today/help.'
        ),
        'question': 'Who is one person you could message today?',
        'prayer': 'Lord, I feel alone. Thank you that you are near to the brokenhearted. Help me sense that you are with me today, and lead me to one person I can talk to. In Jesus’ name, amen.',
    },
    11: {
        'title': 'When you want to give up',
        'opening': (
            'Maybe you are close to quitting something: a course, a job, a habit you have been working on, or a hard conversation you keep trying to have. Some days the effort feels pointless.\n\n'
            'Before you decide anything big, give it one more day. Today, pick the smallest part of the task that you can do in 10 minutes, and do only that. Then rest.'
        ),
        'verse': 'Let’s not be weary in doing good, for we will reap in due season if we don’t give up.',
        'verse_ref': 'Galatians 6:9',
        'after': (
            'Paul wrote to people who were tired of doing good with little to show for it. He promises a harvest “in due season”, a farmer’s way of saying that growing takes time. You might be close to seeing results, or still far away. Either way, one small step today counts.\n\n'
            'If giving up has started to mean giving up on life, please talk to someone today. Call a crisis line in your country now; hopebegins.today/help lists them. If you have felt low most days for weeks, see a doctor or counselor too.'
        ),
        'question': 'What has made you feel like giving up lately?',
        'prayer': 'Lord, I’m tired of trying. Give me strength for one more step today, and patience to wait for what you are growing. In Jesus’ name, amen.',
    },
    12: {
        'title': 'Starting to forgive',
        'opening': (
            'Someone hurt you. Maybe a friend shared something you told them in private, or a coworker took credit for your work. Each time their name comes up, you feel it again. Forgiving can feel unfair, as if you were saying it didn’t matter.\n\n'
            'Today, take ten minutes to write down what happened and how it affected you. You can keep the paper or tear it up afterwards. Then tell God you are willing to start forgiving, even if you don’t feel ready.'
        ),
        'verse': 'bearing with one another, and forgiving each other, if any man has a complaint against any; even as Christ forgave you, so you also do.',
        'verse_ref': 'Colossians 3:13',
        'after': 'Paul ties our forgiving to Christ’s: “even as Christ forgave you, so you also do.” Forgiving means giving up the right to pay them back and leaving the rest with God. It does not mean saying it was fine, and it does not always mean trusting the person again. If someone is still hurting you, getting safe comes first. For most people it happens slowly, through many small decisions.',
        'question': 'Is there someone you could begin to forgive?',
        'prayer': 'Lord Jesus, you forgave me. Help me start to forgive the person who hurt me. Heal what still hurts, and keep me safe. Amen.',
    },
    13: {
        'title': 'Small steps count',
        'opening': (
            'You got out of bed on a morning when it was hard. You drank a glass of water, answered one message and went for a short walk. Nobody noticed. When you feel low, small things like these take real effort, and they are easy to wave away.\n\n'
            'Tonight, before you sleep, write down a few small things you did today. Do it again tomorrow night. After a week, read the whole list. On a hard day, reading it back shows you how much you are already doing.'
        ),
        'verse': 'Indeed, who despises the day of small things?',
        'verse_ref': 'Zechariah 4:10',
        'after': 'Zechariah spoke to people rebuilding the temple in Jerusalem after it had been destroyed. The new foundation looked small next to what they remembered, and some people looked down on it. God’s question to them shows that small beginnings matter to him. Your small steps matter to him too. People usually change through many ordinary days, one small step after another.',
        'question': 'What is one small thing you did today?',
        'prayer': 'Lord, thank you for every small step, including the ones nobody saw. Help me keep going, one day at a time. In Jesus’ name, amen.',
    },
    14: {
        'title': 'Starting again',
        'opening': (
            'Two weeks of Daily Hope are behind you. Some days may have gone well and others not. Maybe you meant to try something and never got to it. That is normal, and a missed day doesn’t cancel what you have done.\n\n'
            'Today is a good day to start again. Pick one thing from the past two weeks that helped, like the slow breathing or the worry list, and do it once today.'
        ),
        'verse': 'Behold, I will do a new thing. It springs out now. Don’t you know it? I will even make a way in the wilderness, and rivers in the desert.',
        'verse_ref': 'Isaiah 43:19',
        'after': 'Isaiah spoke to people far from home, in exile, who thought their story was over. God told them he was doing a new thing and would make “a way in the wilderness”. A wilderness is a place with no clear road, and God promises to make one. You can start again today without a perfect record, as many times as you need to.',
        'question': 'What would a fresh start look like for you today?',
        'prayer': 'Lord, thank you that I can start again with you. Make a way through the places where I feel lost, and give me what I need for today. In Jesus’ name, amen.',
    },
    15: {
        'title': 'Made for good things',
        'opening': (
            'Some weeks you get up, go to work or school, eat, scroll and sleep, and then do it all again. Life starts to feel like a loop, and you wonder whether any of it matters. Purpose can sound big and far away, like something other people have.\n\n'
            'Today, do one small good thing for someone else on purpose. Send a thank-you message to someone who helped you, or listen to a friend without checking your phone. It can take less than ten minutes.'
        ),
        'verse': 'For we are his workmanship, created in Christ Jesus for good works, which God prepared before that we would walk in them.',
        'verse_ref': 'Ephesians 2:10',
        'after': 'Paul says we are God’s “workmanship”, made for good works that God prepared ahead of time. Most of those works are ordinary, like kindness at home or honest work. The good God has in mind for you is often in the day you already have.',
        'question': 'Where might God be using you right now, in your ordinary days?',
        'prayer': 'God, thank you for making me with a purpose. Open my eyes to the good I can do today, and help me do it. In Jesus’ name, amen.',
    },
    16: {
        'title': 'When you feel overlooked',
        'opening': (
            'You weren’t picked for the promotion, or you weren’t invited when everyone else seemed to be. Maybe you are the one in the family nobody asks about. Being passed over again and again can change how you see yourself.\n\n'
            'Today, notice when you think something like “nobody would choose me”. When the thought comes, stop and read the verse below again, slowly.'
        ),
        'verse': 'But you are a chosen race, a royal priesthood, a holy nation, a people for God’s own possession, that you may proclaim the excellence of him who called you out of darkness into his marvelous light.',
        'verse_ref': '1 Peter 2:9',
        'after': 'Peter wrote to Christians who were scattered and looked down on, with no power or status. He told them they were chosen by God, his own people. God chose you because he decided to love you, before you had anything to offer. People may still overlook you sometimes, and it will still hurt. They don’t decide what you are worth. God has already said what you are worth to him.',
        'question': 'Where have you been feeling overlooked lately?',
        'prayer': 'Father, when I feel overlooked, help me remember that you chose me and call me your own through Jesus. Help me live from that today. Amen.',
    },
    17: {
        'title': 'Strength for today',
        'opening': (
            'Strength often looks ordinary. It can mean going to work after a sleepless night, taking your medicine, getting the kids to school, or asking for help when you would rather hide. Nobody posts about these things, and they still take strength.\n\n'
            'Today, write down one hard thing you did in the past month that you haven’t given yourself credit for. Keep the note where you will see it this week, on your phone’s lock screen or on the fridge.'
        ),
        'verse': 'I can do all things through Christ who strengthens me.',
        'verse_ref': 'Philippians 4:13',
        'after': 'Paul wrote this line in a thank-you letter. The verses just before it are about learning to be content with little or with plenty, and the verses after it thank the church in Philippi for the help they sent him. So “all things” here means facing whatever comes, hunger or plenty, with Christ’s help. Asking God for strength and asking people for help go together. Both are ways of not carrying everything on your own.',
        'question': 'When have you been stronger than you thought?',
        'prayer': 'Lord Jesus, be my strength today. Help me lean on you, and on the people you have put around me. Amen.',
    },
    18: {
        'title': 'Your story matters',
        'opening': (
            'Your life might feel ordinary: the same commute, the same routine, and a past with some chapters you would rather skip. It’s easy to think your story doesn’t count for much. Yet the people who help us most are often the ones who can say, “I’ve been there.”\n\n'
            'Today, think of one hard time you came through. Write a few lines about what helped you then. If you know someone going through something similar, think about sending them a message this week.'
        ),
        'verse': 'We know that all things work together for good for those who love God, for those who are called according to his purpose.',
        'verse_ref': 'Romans 8:28',
        'after': 'Paul knew pain well. By the time he wrote this letter he had been in prison and had survived shipwrecks. His promise is that God works all things together for good for those who love him, including the parts we would never choose. God can use your hard chapters too, sometimes to help someone else hold on.',
        'question': 'What part of your story could help someone else?',
        'prayer': 'Lord, take my whole story, the hard parts too, and use it for good. Through Jesus, amen.',
    },
    19: {
        'title': 'Letting others help',
        'opening': (
            'You might be the one everybody leans on, the friend who listens or the one who says “I’m fine” before anyone asks. Carrying it all by yourself gets heavy.\n\n'
            'Today, ask one person for one specific thing. It could be “Can you pray for me this week?” or “Can you watch the kids for an hour tonight?”'
        ),
        'verse': 'Bear one another’s burdens, and so fulfill the law of Christ.',
        'verse_ref': 'Galatians 6:2',
        'after': (
            'Paul tells the church to carry each other’s burdens. That assumes everyone has burdens and everyone needs help sometimes, including the people who look strong. Letting someone help you is part of how the church is meant to work. You can also ask someone to pray for you at hopebegins.today/prayers.\n\n'
            'If the weight has lasted for weeks, talk to a doctor or counselor. If you are thinking of ending your life, call a crisis line in your country now; hopebegins.today/help lists them.'
        ),
        'question': 'Who is one person you could open up to this week?',
        'prayer': 'Lord, I don’t want to carry this by myself. Give me the courage to ask for help, and lead me to people I can trust. In Jesus’ name, amen.',
    },
    20: {
        'title': 'When God seems quiet',
        'opening': (
            'You have prayed about the same thing for months. You keep checking your phone for the call or the result you are waiting for, and nothing comes. When God seems quiet, it’s easy to wonder if he has stopped listening.\n\n'
            'Today, look further back than this week. Write down one prayer from a year or more ago and what happened with it, even if the answer was different from what you asked for.'
        ),
        'verse': 'being confident of this very thing, that he who began a good work in you will complete it until the day of Jesus Christ.',
        'verse_ref': 'Philippians 1:6',
        'after': 'Paul wrote this letter from prison, with his own future uncertain. He was still sure that God finishes what he starts. Waiting can feel like nothing is happening. In the Bible, waiting is often when God does slow, quiet work in people. He has not left your life half done.',
        'question': 'Where have you been wondering if God is still with you?',
        'prayer': 'Father, I have been waiting a long time. Help me trust that you are still at work in me and in this situation. Keep my faith steady while I wait. In Jesus’ name, amen.',
    },
    21: {
        'title': 'Three weeks on',
        'opening': 'This is your last Daily Hope email. Three weeks ago you signed up, maybe on a hard day. Today, take ten minutes to look back. Read the notes you wrote, if you kept them. Then write down what is different now, even a little, like something you handle better or a habit you started. Change is slow and hard to see from the inside, so writing it down helps.',
        'verse': 'But we all, with unveiled face seeing the glory of the Lord as in a mirror, are transformed into the same image from glory to glory, even as from the Lord, the Spirit.',
        'verse_ref': '2 Corinthians 3:18',
        'after': (
            'Paul says we are being changed “from glory to glory”. The words describe something still going on: God keeps changing us, little by little, as we look to Jesus. Keep doing the small things that helped you over these three weeks.\n\n'
            'HopeBegins is still there when you need it. You can make a free personal plan at hopebegins.today/action-plan, ask someone to pray for you at hopebegins.today/prayers, or find free help in your country at hopebegins.today/help.'
        ),
        'question': 'How have you changed in the past three weeks?',
        'prayer': 'Lord, thank you for these three weeks and for the work you are doing in me. Keep making me more like Jesus, one day at a time. Amen.',
    },
}
