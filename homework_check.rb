path = ENV['ELSYS_HOMEWORK'] || ARGV[0]
homewok = ARGV[1] || "02"
Dir["#{path}#{homewok}/*.c"].each do |file|
	# p file
	command = "/usr/bin/gcc #{file} -Wall -pedantic"
	# stdout, stderr, pipes
	rout, wout = IO.pipe
	rerr, werr = IO.pipe

	pid = Process.spawn(command, :out => wout, :err => werr)
	_, status = Process.wait2(pid)

	# close write ends so we could read them
	wout.close
	werr.close

	@stdout = rout.readlines.join("\n")
	@stderr = rerr.readlines.join("\n")
	# p @stdout
	p @stderr
	# dispose the read ends of the pipes
	rout.close
	rerr.close

	@last_exit_status = status.exitstatus
end