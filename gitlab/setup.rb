root_user = User.find_by_username("root")

if !root_user.nil?
	puts "Found root user"
else
	puts "Couldn't find root user"
	exit 1
end

if !ENV["ADMIN_ACCESS_TOKEN"].nil?
	puts "Setting admin access token"
	tokens = root_user.personal_access_tokens
	already_exists = false
	tokens.each do |token|
		if token.name == "ADMIN_ACCESS_TOKEN"
			already_exists = true
		end	
	end
	if already_exists
		puts "ADMIN_ACCESS_TOKEN is already set. Not setting!"
	else
		puts "Setting ADMIN_ACCESS_TOKEN"
		token = tokens.create(scopes: [:api, :read_api, :read_user, :read_repository, :write_repository, :sudo],name: "ADMIN_ACCESS_TOKEN" )
		token.set_token(ENV["ADMIN_ACCESS_TOKEN"])
		token.save!
	end

end

if !ENV["ROOT_PASSWORD"].nil?
	puts "Setting root user password"
	root_user.password = ENV["ROOT_PASSWORD"]
	root_user.password_confirmation = ENV["ROOT_PASSWORD"]
	root_user.save!
	puts "Changed root user password"
end

already_exists = false
SystemHook.all.each do |hook|
	if hook.url == ENV["SYSTEM_HOOK_URL"]
		already_exists = true
	end
end
if already_exists
	puts "System hook already exists. Not setting!"
else
	puts "Creating System hook"
	hook = SystemHook.create(url: ENV["SYSTEM_HOOK_URL"],token: ENV["SYSTEM_HOOK_SECRET"],enable_ssl_verification: false,tag_push_events: true)
	hook.save!
end