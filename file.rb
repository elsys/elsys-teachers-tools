# 1.upto(29) do |number|
# 	3.upto(6) do |hw|
# 		number_in_class = number.between?(1, 9) ? "0#{number}" : number
# 		system( "evaluator /home/tsvetelina/elsys/po-homework/2015-2016/B/#{number_in_class}/0#{hw} /home/tsvetelina/elsys/asen/elsys-teachers-tools/data/evaluator/scenarios/A_B_class/0#{hw}.toml -l DEBUG")
# 	end
# end

1.upto(30) do |number|
	3.upto(8) do |hw|
		number_in_class = number.between?(1, 9) ? "0#{number}" : number
		system( "evaluator /home/tsvetelina/elsys/po-homework/2015-2016/G/#{number_in_class}/0#{hw} /home/tsvetelina/elsys/asen/elsys-teachers-tools/data/evaluator/scenarios/V_G_class/0#{hw}.toml -l DEBUG")
	end
end

