package ssh

type ExecuteRequest struct {
	Command        string `json:"command"`
	ExecuteTimeout int    `json:"execute_timeout"`
	Host           string `json:"host"`
	User           string `json:"user"`
	Password       string `json:"password"`
}

type ExecuteResponse struct {
	Output     string `json:"output"`
	InstanceId string `json:"instance_id"`
	Success    bool   `json:"success"`
}
