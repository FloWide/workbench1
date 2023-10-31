local opts = require('.etc.openresty.auth.oidc')

local function get_token()
  local token = ngx.var.arg_token

  if token == nil then
      token = ngx.var.cookie_token
  end

  if token == nil then
      local auth_header = ngx.var.http_Authorization
      if auth_header then
          _, _, token = string.find(auth_header, "Bearer%s+(.+)")
      end
  end

  return token
end

local function try_sso_login()
  local action = "deny"
  if ngx.var.http_accept then
    for ct in (ngx.var.http_accept .. ","):gmatch("([^,]*),") do
      if string.sub(ct, 0, 9) == "text/html" then
        action = null
        break
      end
    end
  end

  local res, err = require("resty.openidc").authenticate(opts, null, action)
  if err then
    ngx.status = 403
    ngx.exit(ngx.HTTP_FORBIDDEN)
  end

end

local function verify_token(token)
  local json,err = require("resty.openidc").jwt_verify(token,opts)
  if err then
    ngx.print(err)
  end
  return not (err or not json)
end


local token = get_token()

if token == nil then
  try_sso_login()
else
  if not verify_token(token)  then
    ngx.status = 403
    ngx.exit(ngx.HTTP_FORBIDDEN)
  else
    ngx.header["Set-Cookie"] = "token=" .. token .. ";HttpOnly;Secure;Path=/streamlit-cloud;SameSite=Lax"
  end
end

