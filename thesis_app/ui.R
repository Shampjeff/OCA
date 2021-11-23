### UI ###
library(shiny)

ui <- fluidPage(
  tabsetPanel(
    tabPanel("Bail Setting Patterns by Charge",
             titlePanel("Bail Setting Patterns In New York City"),
             
             verticalLayout(selectInput(inputId="article_section", 
                             label="Choose an Article and Section", 
                             choices=c(top_arraign_char), 
                             selected = "265.03"),
                            textOutput("description"),
                            textOutput("text")),
             br(),
             
             mainPanel(
               fluidRow(column(width = 12,
                  plotOutput("bail_time",
                          width = "100%"))),
               br(),
               fluidRow(column(width = 12,
                  plotOutput("bail_histo_race",
                          width = "100%"))),
               br(),
               br(),
               fluidRow(column(width = 12,
                  plotOutput("bail_by_priors",
                          width = "100%")))
               )
             ),
    
    tabPanel("Bail Setting Patterns by Judge",
             titlePanel("Bail Setting Patterns In New York City"),

             verticalLayout(selectInput(inputId="article_section_2", 
                                        label="Choose an Article and Section", 
                                        choices=c(top_arraign_char), 
                                        selected = "265.03"),
                            textOutput("description_2"),
                            textOutput("text_2")
                            ),
              br(),

             fluidRow(column(width = 12,
                             plotOutput("judge_most",
                                width = "100%"))),
             fluidRow(column(width = 12,
                               plotOutput("judge_least",
                                  width = "100%"))),
             br(),
             splitLayout(plotOutput("histo_most",
                                  width="100%"),
                        plotOutput("histo_least",
                                  width="100%")),

             selectInput(inputId="judge",
                         label="Choose a Judge",
                         choices = c(all_judge_vec),
                         selected = "walsh, jean t."),
             
             fluidRow(column(width = 12,
                             plotOutput("judge_atl_sec",
                                        width = "100%")))

             )
    )
  )
   