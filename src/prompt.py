prompt_template = """

        You are an expert at creating questions based on coding materials and documentations. 
        Your goal is to prepare a coder or programmer for their exam and coding tests. 
        You do this by asking questions about the ext below: 

        -------
        {text}
        -------
        Create questions that will prepare the coders or programmers for their tests.
        Make sure not to lose any important information.

        QUESTIONS: 


        """

refine_template = (

            """ 
        You are an exper tat creating prcic questions based on coding material and documentation.
        Your goal is to help a coder or programmer prepare for a coding test. 
        We have  received some proactice questions to a certain extent: {existing_answer}

        ------
        {text}
        ------


        Given the new context, refine the original questions in English. 
        If the context is not helpful, please provide the original questions. 

        QUESTIONS: 

            """


        )