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

	log.Println("Waiting for messages...")
	select {}
}

func subscribeSSHExecutor(nc *nats.Conn, instanceId *string) {
	subject := fmt.Sprintf("ssh.execute.%s", *instanceId)
	log.Printf("Subscribing to subject: %s", subject)
	nc.Subscribe(subject, func(msg *nats.Msg) {
		var sshExecuteRequest ssh.ExecuteRequest
		if err := json.Unmarshal(msg.Data, &sshExecuteRequest); err != nil {
			log.Printf("Error unmarshalling message: %v", err)
			return
		}
		log.Printf("Received a message: %s", sshExecuteRequest.Command)
		responseData := ssh.Execute(sshExecuteRequest, *instanceId)
		log.Printf("Publishing response to subject: ssh.execute.response")

		responseContent, _ := json.Marshal(responseData)
		if err := nc.Publish("ssh.execute.response", responseContent); err != nil {
			log.Printf("Error publishing response: %v", err)
		}
	})
}

func subscribeLocalExecutor(nc *nats.Conn, instanceId *string) {
	subject := fmt.Sprintf("local.execute.%s", *instanceId)
	log.Printf("Subscribing to subject: %s", subject)
	nc.Subscribe(subject, func(msg *nats.Msg) {
		var localExecuteRequest local.ExecuteRequest
		if err := json.Unmarshal(msg.Data, &localExecuteRequest); err != nil {
			log.Printf("Error unmarshalling message: %v", err)
			return
		}
		log.Printf("Received a message: %s", localExecuteRequest.Command)
		responseData := local.Execute(localExecuteRequest, *instanceId)
		log.Printf("Publishing response to subject: local.execute.response")

		responseContent, _ := json.Marshal(responseData)
		if err := nc.Publish("local.execute.response", responseContent); err != nil {
			log.Printf("Error publishing response: %v", err)
		}
	})
}
