package models

type Pathogen struct {
	Name 		string `json:"name" db:"name"`
	AuthorID 	int `json:"author_id" db:"author_id"`
	AuthorName  string `json:"author_name" db:"author_name"`
	UpdateDate  int64 `json:"upd_date" db:"upd_date"`
}