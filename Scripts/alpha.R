library(ggplot2)

df <- read.csv("budget-vs-alpha.csv")

p <- ggplot(df, aes(budget, alpha)) + geom_line(color="red")
p <- p + labs(title = "Fraction of unstopped attacks as function of privacy budget")
p <- p + labs(y = "Fraction of unstopped Attacks (α)") + labs(x = "Attacker's Privacy budget (bits)")
p <- p + scale_x_continuous(expand=c(0,0), limits = c(0, 16)) + 
  scale_y_continuous(expand=c(0,0), limits = c(0, 1))

p <- p + theme(
  panel.background = element_rect(fill = NA),
  panel.grid.major = element_line(colour = NA),
  axis.line = element_line(size = 0.5, colour = "black"),
)

print(p)
ggsave("budget-vs-alpha.png", width=6, height=3)
