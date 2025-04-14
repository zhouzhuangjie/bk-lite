package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"github.com/nats-io/nats.go"
	"log"
	"nats-executor/local"
	"nats-executor/ssh"
)

func main() {
	var urls = flag.String("s", nats.DefaultURL, "The nats server URLs (separated by comma)")
	var instanceId = flag.String("i", "1", "The instance id")
	flag.Parse()

	log.Printf("Connecting to NATS server at %s", *urls)
	opts := []nats.Option{
		nats.Name("nats-executer"),
		nats.Compression(true),
	}
	nc, err := nats.Connect(*urls, opts...)
	if err != nil {
		log.Fatalf("Failed to connect to NATS server: %v", err)
	}
	defer nc.Close()
	log.Println("Connected to NATS server")

	subscribeLocalExecutor(nc, instanceId)
	subscribeSSHExecutor(nc, instanceId)

	subscribeDownloadToLocal(nc, instanceId)
	subscribeDownloadToRemote(nc, instanceId)

	log.Println("Waiting for messages...")
	select {}
}

func subscribeLocalExecutor(nc *nats.Conn, instanceId *string) {
	subject := fmt.Sprintf("local.execute.%s", *instanceId)
	log.Printf("Subscribing to subject: %s", subject)
	nc.Subscribe(subject, func(msg *nats.Msg) {
		// 定义一个临时结构来接收请求方格式
		var incoming struct {
			Args   []json.RawMessage      `json:"args"`
			Kwargs map[string]interface{} `json:"kwargs"`
		}

		if err := json.Unmarshal(msg.Data, &incoming); err != nil {
			log.Printf("Error unmarshalling incoming message: %v", err)
			return
		}

		if len(incoming.Args) == 0 {
			log.Printf("No arguments received")
			return
		}
		var localExecuteRequest local.ExecuteRequest
		if err := json.Unmarshal(incoming.Args[0], &localExecuteRequest); err != nil {
			log.Printf("Error unmarshalling first arg to local.ExecuteRequest: %v", err)
			return
		}

		log.Printf("Received command: %s", localExecuteRequest.Command)
		responseData := local.Execute(localExecuteRequest, *instanceId)
		log.Printf("Publishing response to subject: local.execute.response")

		responseContent, _ := json.Marshal(responseData)
		if err := msg.Respond(responseContent); err != nil {
			log.Printf("Error publishing response: %v", err)
		}

	})
}

func subscribeSSHExecutor(nc *nats.Conn, instanceId *string) {
	subject := fmt.Sprintf("ssh.execute.%s", *instanceId)
	log.Printf("Subscribing to subject: %s", subject)
	nc.Subscribe(subject, func(msg *nats.Msg) {
		// 解析 request 的标准结构
		var incoming struct {
			Args   []json.RawMessage      `json:"args"`
			Kwargs map[string]interface{} `json:"kwargs"`
		}

		if err := json.Unmarshal(msg.Data, &incoming); err != nil {
			log.Printf("Error unmarshalling incoming message: %v", err)
			return
		}

		if len(incoming.Args) == 0 {
			log.Printf("No arguments received")
			return
		}

		var sshExecuteRequest ssh.ExecuteRequest
		if err := json.Unmarshal(incoming.Args[0], &sshExecuteRequest); err != nil {
			log.Printf("Error unmarshalling first arg to ssh.ExecuteRequest: %v", err)
			return
		}

		log.Printf("Received SSH command: %s", sshExecuteRequest.Command)
		responseData := ssh.Execute(sshExecuteRequest, *instanceId)
		log.Printf("Publishing SSH response using msg.Respond")

		responseContent, _ := json.Marshal(responseData)
		if err := msg.Respond(responseContent); err != nil {
			log.Printf("Error responding to SSH request: %v", err)
		}
	})
}

func subscribeDownloadToLocal(nc *nats.Conn, instanceId *string) {
	subject := fmt.Sprintf("download.local.%s", *instanceId)
	log.Printf("Subscribing to subject: %s", subject)

	nc.Subscribe(subject, func(msg *nats.Msg) {
		// 解析 request 的标准结构
		var incoming struct {
			Args   []json.RawMessage      `json:"args"`
			Kwargs map[string]interface{} `json:"kwargs"`
		}

		if err := json.Unmarshal(msg.Data, &incoming); err != nil {
			log.Printf("Error unmarshalling incoming message: %v", err)
			return
		}

		if len(incoming.Args) == 0 {
			log.Printf("No arguments received")
			return
		}

		// 解析 DownloadFileRequest
		var downloadRequest local.DownloadFileRequest

		if err := json.Unmarshal(incoming.Args[0], &downloadRequest); err != nil {
			log.Printf("Error unmarshalling first arg to DownloadFileRequest: %v", err)
			return
		}

		log.Printf("Starting download from bucket %s, file %s to local path %s", downloadRequest.BucketName, downloadRequest.FileKey, downloadRequest.TargetPath)
		resp := local.DownloadFile(downloadRequest, nc, *instanceId)
		if !resp.Success {
			log.Printf("Error downloading file: %s", resp.Output)
			return
		}

		log.Printf("File downloaded successfully to %s", downloadRequest.TargetPath)
		responseData := map[string]interface{}{
			"success": true,
		}

		// 发布响应
		responseContent, _ := json.Marshal(responseData)
		if err := msg.Respond(responseContent); err != nil {
			log.Printf("Error responding to download request: %v", err)
		}
	})
}

func subscribeDownloadToRemote(nc *nats.Conn, instanceId *string) {
	subject := fmt.Sprintf("download.remote.%s", *instanceId)
	log.Printf("Subscribing to subject: %s", subject)

	nc.Subscribe(subject, func(msg *nats.Msg) {
		var incoming struct {
			Args   []json.RawMessage      `json:"args"`
			Kwargs map[string]interface{} `json:"kwargs"`
		}

		if err := json.Unmarshal(msg.Data, &incoming); err != nil {
			log.Printf("Error unmarshalling incoming message: %v", err)
			return
		}

		if len(incoming.Args) == 0 {
			log.Printf("No arguments received")
			return
		}

		var downloadRequest ssh.DownloadFileRequest

		if err := json.Unmarshal(incoming.Args[0], &downloadRequest); err != nil {
			log.Printf("Error unmarshalling first arg to DownloadFileRequest: %v", err)
			return
		}

		log.Printf("Starting download from bucket %s, file %s to local path %s", downloadRequest.BucketName, downloadRequest.FileKey, downloadRequest.TargetPath)

		// Step 1: 下载文件到本地
		localdownloadRequest := local.DownloadFileRequest{
			BucketName:     downloadRequest.BucketName,
			FileKey:        downloadRequest.FileKey,
			FileName:       downloadRequest.FileName,
			TargetPath:     downloadRequest.TargetPath,
			ExecuteTimeout: downloadRequest.ExecuteTimeout,
		}

		resp := local.DownloadFile(localdownloadRequest, nc, *instanceId)
		if !resp.Success {
			log.Printf("Error downloading file: %s", resp.Output)
			return
		}

		// 使用sshpass处理带密码的scp传输
		scpCommand := fmt.Sprintf("sshpass -p '%s' scp -o StrictHostKeyChecking=no %s/%s %s@%s:%s",
			downloadRequest.Password,
			localdownloadRequest.TargetPath,
			localdownloadRequest.FileName,
			downloadRequest.User,
			downloadRequest.Host,
			downloadRequest.TargetPath)

		localExecuteRequest := local.ExecuteRequest{
			Command:        scpCommand,
			ExecuteTimeout: downloadRequest.ExecuteTimeout,
		}

		log.Printf("Starting file transfer to remote host: %s@%s:%s", downloadRequest.User, downloadRequest.Host, downloadRequest.TargetPath)
		responseData := local.Execute(localExecuteRequest, *instanceId)

		responseContent, _ := json.Marshal(responseData)
		if err := msg.Respond(responseContent); err != nil {
			log.Printf("Error responding to download request: %v", err)
		}
	})
}
