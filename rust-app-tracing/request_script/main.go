package main

import (
	"fmt"
	"math/rand"
	"net/http"
	"time"
)

func main() {
	rand.Seed(time.Now().UnixNano())
	min := 3
	max := 8
	for range time.Tick(time.Second * 1) {
		at_most := rand.Intn(max-min+1) + min
		make_requests(at_most)
	}
}

func make_requests(max int) {
	i := 0
	for i < max {
		go request(i)
		i += 1
	}
}

func request(num int) {
	_, err := http.Get("http://localhost:9000/posts")
	if err != nil {
		fmt.Printf("request `%d` error \n", num)
	} else {
		fmt.Printf("request `%d` ok \n", num)
	}
}
