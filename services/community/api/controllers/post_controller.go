/*
 * Licensed under the Apache License, Version 2.0 (the “License”);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an “AS IS” BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package controllers

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
	"strconv"

	"crapi.proj/goservice/api/models"
	"crapi.proj/goservice/api/responses"
	"github.com/gorilla/mux"
)

// AddNewPost add post in database,
// @return HTTP Status
// @params ResponseWriter, Request
// Server have database connection
func (s *Server) AddNewPost(w http.ResponseWriter, r *http.Request) {

	body, err := io.ReadAll(r.Body)
	defer func() {
		if err := r.Body.Close(); err != nil {
			log.Println("Error closing request body:", err)
		}
	}()
	if err != nil {
		responses.ERROR(w, http.StatusBadRequest, err)
		return
	}
	post := models.Post{}

	err = json.Unmarshal(body, &post)
	if err != nil {
		responses.ERROR(w, http.StatusBadRequest, err)
		return
	}
	post.Prepare()

	savedPost, err := models.SavePost(s.Client, post)
	if err != nil {
		responses.ERROR(w, http.StatusInternalServerError, err)
	}

	responses.JSON(w, http.StatusOK, savedPost)
}

// GetPostByID fetch the post by ID,
// @return HTTP Status
// @params ResponseWriter, Request
// Server have database connection
func (s *Server) GetPostByID(w http.ResponseWriter, r *http.Request) {

	vars := mux.Vars(r)
	//var autherID uint64
	GetPost, er := models.GetPostByID(s.Client, vars["postID"])
	if er != nil {
		responses.ERROR(w, http.StatusBadRequest, er)
	}

	responses.JSON(w, http.StatusOK, GetPost)

}

// GetPost Vulnerabilities
func (s *Server) GetPost(w http.ResponseWriter, r *http.Request) {
	//post := models.Post{}
	limit_param := r.URL.Query().Get("limit")
	var limit int64 = 30
	err := error(nil)
	if limit_param != "" {
		// Parse limit_param and set to limit
		limit, err = strconv.ParseInt(limit_param, 10, 64)
		if err != nil {
			limit = 30
		}
	}
	if limit > 50 {
		limit = 50
	}

	var offset int64 = 0
	offset_param := r.URL.Query().Get("offset")
	if offset_param != "" {
		offset, err = strconv.ParseInt(offset_param, 10, 64)
		if err != nil {
			offset = 0
		}
	}
	posts, err := models.FindAllPost(s.Client, offset, limit)

	if err != nil {
		responses.ERROR(w, http.StatusInternalServerError, err)
		return
	}
	responses.JSON(w, http.StatusOK, posts)
}

// Comment will add comment in perticular post,
// @return HTTP Post Object
// @params ResponseWriter, Request
// Server have database connection
func (s *Server) Comment(w http.ResponseWriter, r *http.Request) {

	vars := mux.Vars(r)
	body, err := io.ReadAll(r.Body)
	defer func() {
		if err := r.Body.Close(); err != nil {
			log.Println("Error closing request body:", err)
		}
	}()
	if err != nil {
		responses.ERROR(w, http.StatusBadRequest, err)
		return
	}
	comment := models.Comments{}

	err = json.Unmarshal(body, &comment)
	if err != nil {
		responses.ERROR(w, http.StatusBadRequest, err)
		return
	}
	if vars["postID"] == "" {
		responses.ERROR(w, http.StatusBadRequest, err)
		return
	}
	comment.ID = vars["postID"]
	postData, er := models.CommentOnPost(s.Client, comment)
	if er != nil {
		responses.ERROR(w, http.StatusInternalServerError, er)
		return
	}
	responses.JSON(w, http.StatusOK, postData)
}
